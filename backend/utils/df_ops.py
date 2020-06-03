import numpy as np
import pandas as pd
from random import randint
from statistics import mode
from datetime import datetime
import backend.utils.finder as finder
from dateutil.relativedelta import relativedelta


def arrange_df(df, df_type, relevant_col_idx=None, items_to_delete=None, assembly_df=None, bom_trim=False):
    """
    :param bom_trim:
    :param df:
    pandas.DataFrame object that contains the raw format that is read from the file.
    :param df_type:
    File type of
    :param relevant_col_idx:
    :param items_to_delete:
    :param assembly_df:
    :return:
    """
    df = df.copy()
    if df_type.lower() == "bom":
        # Reformatting the columns
        df = reformat_columns(df, relevant_col_idx, "bom")

        # If specified, bom will be trimmed
        if bom_trim:
            df = trim_bom(df)

        # This part will be discarded for the time being, 15.04.2020
        # Deleting the trial products
        # df.drop(df[df.product_no.str.split(".", 0).apply(lambda x: int(x[2]) > 900)].index, inplace = True)

        # Deleting the entries where two successive entries are level 1s.
        df.drop(df[df.level.eq(df.level.shift(-1, fill_value=1)) & df.level.eq(1)].index, inplace=True)

        # This to be deleted parts can be redundant, so it will be decided that if these codes are going to stay or not
        tbd_list = items_to_delete["Silinecekler"].unique().tolist()
        df.drop(df[df["part_no"].str.split(".").apply(lambda x: x[0] in tbd_list)].index, inplace=True)

        # Deleting the entries where two successive entries are level 1s.
        df.drop(df[df.level.eq(df.level.shift(-1, fill_value=1)) & df.level.eq(1)].index, inplace=True)

        # Check if the product structure is okay or not, if not okay, delete the corresponding products from the BOM
        df.drop(df[df.groupby("product_no").apply(corrupt_product_bom).values].index, inplace=True)

        # Transforming the amounts to a desired format for the simulation model.
        df.amount = determine_amounts(df)

        # Making sure that the dataframe returns in order
        df.reset_index(drop=True, inplace=True)

        return df

    if df_type.lower() == "times":
        # Reformatting the columns
        df = reformat_columns(df, relevant_col_idx, "times")

        # Transforming the machine names to ASCII characters.
        df["station"] = format_machine_names(df, "station")

        # Transforming non-numeric values to numeric values
        df.cycle_times = pd.to_numeric(df.cycle_times, errors="coerce").fillna(0)
        df.setup_times = pd.to_numeric(df.setup_times, errors="coerce").fillna(0)

        # Grouping by the times of the parts that has multiple times in the same work station
        df = df.groupby(["part_no", "station"], as_index=False).agg({"cycle_times": sum, "setup_times": max})
        df.drop(df[df["part_no"].duplicated(keep="last")].index, inplace=True)

        # Creating the setup matrix
        set_list_df = df[["station", "setup_times"]].copy()
        set_list_df.columns = ["stations_list", "setup_time"]
        set_list_df = set_list_df.groupby(by="stations_list", as_index=False).agg({"setup_time": mode})
        set_list_df["setup_prob"] = 1
        set_list_df.loc[(set_list_df.stations_list == "ANKASTRE_BOYAHANE") |
                        (set_list_df.stations_list == "ENDUSTRI_BOYAHANE"), "setup_prob"] = 3 / 100
        set_list_df.loc[set_list_df.stations_list == "ANKASTRE_BOYAHANE", "setup_time"] = 900
        set_list_df.loc[set_list_df.stations_list == "ENDUSTRI_BOYAHANE", "setup_time"] = 1200

        # Creating a dataframe with the assembly times
        montaj_df = df[(df["station"] == "BANT") | (df["station"] == "LOOP")]

        # Creating a dataframe with the glass bonding
        cmy_df = df[df["station"] == "CAM_YAPISTIRMA"]

        # Dropping the assembly times from the original times dataframe and resetting the index
        df.drop(df[(df["station"] == "BANT") |
                   (df["station"] == "LOOP") |
                   (df["station"] == "CAM_YAPISTIRMA") |
                   (df["part_no"].apply(lambda x: len(x)) == 13)].index, inplace=True)

        # Resetting the index
        df.reset_index(drop="index", inplace=True)

        # Getting rid of the setup column of time matrix
        # df.drop("setup_times", axis = 1, inplace = True)

        return df, montaj_df, cmy_df, set_list_df

    if df_type.lower() == "merged":
        df["station"] = level_lookup(df, "level", "station")
        df["cycle_times"] = level_lookup(df, "level", "cycle_times")

        df.loc[df.level == 1, ["station", "cycle_times"]] = \
            pd.merge(df["product_no"], assembly_df[["part_no", "station", "cycle_times"]], "left",
                     left_on="product_no",
                     right_on="part_no")[["station", "cycle_times"]]

        missing_dict = missing_values_df(df)
        missing_df = pd.DataFrame(missing_dict).transpose().reset_index()
        missing_df.columns = ["code", "station", "cycle_times"]
        # Ask for what are the values for the NAs in the missing dictionary
        """
        THIS WILL CHANGE
        """
        missing_df.station.fillna("CAM_YAPISTIRMA", inplace=True)
        missing_df.cycle_times.fillna(np.random.randint(25, 60), inplace=True)
        """
        END OF THIS WILL CHANGE
        """
        # Rounding all the numerical values to integers.
        missing_df.loc[~missing_df.station.isna(), "cycle_times"] = \
            missing_df.loc[~missing_df.station.isna(), "cycle_times"].apply(np.ceil)

        # Creating the missing slice to fill it to the merged bom dataframe later
        missing_slice = pd.merge(left=df[df.station.isna()].part_no.str.split(".").apply(lambda x: x[0]),
                                 right=missing_df, left_on="part_no", right_on="code", how="left")
        missing_slice.index = df.loc[df.station.isna()].index

        # Equating the filled missing data slice into the bom
        df.loc[df.station.isna(), ["station", "cycle_times"]] = \
            missing_slice[["station", "cycle_times"]]

        return df


def reformat_columns(df, relevant_col_idx, df_type):
    if df_type == "bom":
        df = df.copy()
        # Rearranging the level amount
        df["Seviye"] = [int(str(x)[-1]) for x in df[df.columns[relevant_col_idx][2]]]
        relevant_col_idx[2] = len(df.columns) - 1

        # Determining the columns names to use for reindex later
        relevant_col_names = df.columns[relevant_col_idx]

        # Columns to be dropped from the dataframe
        cols_to_drop = list(set(df.columns) - set(df.columns[relevant_col_idx]))

        # Dropping, sorting and indexing the corresponding columns
        df.drop(cols_to_drop, axis=1, inplace=True)
        df = df.reindex(columns=relevant_col_names)
        df.columns = ["product_no", "part_no", "level", "amount", "explanation"]

    if df_type == "times":
        # Determining the columns names to use for reindex later
        relevant_col_names = df.columns[relevant_col_idx]

        # Columns to be dropped from the dataframe
        cols_to_drop = list(set(df.columns) - set(df.columns[relevant_col_idx]))

        # Dropping, sorting and indexing the corresponding columns
        df.drop(cols_to_drop, axis=1, inplace=True)
        df = df.reindex(columns=relevant_col_names)
        df.columns = ["part_no", "station", "cycle_times", "setup_times"]

    return df


def trim_bom(df):
    # This little piece of code trims the bom so that there is only one instance of product for each product family.
    df["product_family"] = [x.split(".")[0] for x in df.product_no]
    first_products = df[df.product_family.ne(df.product_family.shift(1, fill_value=0))]["product_no"].to_list()
    a = pd.Series([x in first_products for x in df.product_no])
    df.drop(df[~a].index, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # This part is a bit more tricky, this code takes the 90th percentile in the past orders and then takes them into
    # consideration

    # Order data processing and finding 90 Percentile
    # order_data = pd.read_csv("D:/Python/ml/5_yil_uretim.csv")
    # order_data.drop(order_data.columns[1:4], axis = 1, inplace = True)
    # order_data["sum"] = order_data[order_data.columns[1:]].sum(axis = 1)
    # order_data.sort_values(by = "sum", inplace = True, ascending = False)
    # This part drops the items that are not in the demand page, will change later.
    # bom_list = set(df.product_no.to_list())
    # order_list = order_data[order_data.columns[0]].to_list()
    # order_data.drop(order_data[[x not in bom_list for x in order_list]].index, inplace = True)
    # End of that part.
    # order_data["perc"] = order_data["sum"].cumsum()/order_data["sum"].sum().cumsum()
    # order_data.reset_index(drop = True, inplace = True)
    # perc_count = order_data[order_data.perc > 0.9].head(1).index.astype(int)[0]
    # prod_list = order_data[order_data.columns[0]].tolist()
    # perc_list = [x for x in prod_list if x in frozenset(df.product_no.to_list())][:perc_count]
    # a = pd.Series([x in perc_list for x in df.product_no])
    # df.drop(df[~a].index, inplace = True)
    # df.reset_index(drop = True, inplace = True)

    return df


def trim_order(order_df, bom_df):
    order_df = order_df.pivot()
    return order_df[order_df.index.to_series().str.split(".").apply(lambda x: x[0]).isin(
        bom_df.product_no.str.split(".").apply(lambda x: x[0]))]


def trim_df(df, plan_df):
    temp_df = df.copy()
    products_to_be_taken = pd.DataFrame(plan_df.product_no.unique().tolist(), columns=["product_no"])
    products_to_be_taken["is_in_merged"] = products_to_be_taken.product_no.isin(temp_df.product_no.unique().tolist())
    missing_dict = find_most_close_products(products_to_be_taken[products_to_be_taken.is_in_merged.eq(0)], temp_df)
    products_to_be_taken.product_no.replace(missing_dict, inplace=True)
    temp_df = temp_df[temp_df.product_no.isin(products_to_be_taken.product_no.to_list()).eq(1)]
    temp_df.reset_index(drop=True, inplace=True)
    return temp_df, missing_dict


def schedule_changer_dict(df, days):
    current_month = datetime(df.start_date.dt.year.mode(), df.start_date.dt.month.mode(), 1).date()
    availability = [
        1 if (list(days.values)[0][x] == 1) & ((current_month + pd.to_timedelta(x, unit="d")).weekday() < 5) else 0 for
        x in range(0, days.columns.max())]

    replace_dict = {}
    if current_month.weekday() >= 5:
        replace_dict[current_month] = pd.to_datetime(
            (current_month + pd.to_timedelta(7 - current_month.weekday(), unit="d")))
    else:
        replace_dict[current_month] = pd.to_datetime(current_month)
    for x in range(1, days.columns.max()):
        if availability[x] == 1:
            replace_dict[(current_month + pd.to_timedelta(x, unit="d"))] = \
                pd.to_datetime(current_month + pd.to_timedelta(x, unit="d"))
        else:
            replace_dict[(current_month + pd.to_timedelta(x, unit="d"))] = \
                pd.to_datetime(max(replace_dict.values()))

    renewed_dict = {x: replace_dict[x].date() for x in list(replace_dict.keys())}
    # days["day"] = days["date"].dt.day
    # days.day.replace(renewed_dict, inplace = True)
    return renewed_dict


def level_lookup(df, level_col, lookup_col):
    dummies = pd.get_dummies(df[level_col])

    idx = dummies.index.to_series()
    last_index = dummies.apply(lambda col: idx.where(col != 0, np.nan).fillna(method="ffill"))
    last_index[0] = 1

    idx = last_index.lookup(last_index.index, df[level_col] - 1)
    return pd.DataFrame({lookup_col: df.reindex(idx)[lookup_col].values}, index=df.index)


def missing_values_df(df):
    missing_parts = df[df.station.isna()].part_no.str.split(".").apply(lambda x: x[0]).unique()
    missing_dict = {}
    for items in missing_parts:
        temp_station = df[df.part_no.apply(lambda x: x.split(".")[0]) == items].station.mode()
        if temp_station.shape == (0,):
            temp_station = np.nan
        else:
            temp_station = temp_station[0]
        temp_cycle = df[df.part_no.apply(lambda x: x.split(".")[0]) == items].cycle_times.mean()
        missing_dict[items] = [temp_station, temp_cycle]
    return missing_dict


def merge_bom_and_times(df_bom, df_times):
    df = pd.merge(left=df_bom, right=df_times, how="left", on="part_no")
    df = df[list(df.columns[0:4]) + list(df.columns[5:]) + list(df.columns[4:5])].copy()
    return df


def format_word(word, letter_dict):
    new_word = ""
    for i in range(len(word)):
        if word[i] in letter_dict.keys():
            new_word += letter_dict[word[i]].upper()
            continue
        new_word += word[i].upper()
    return new_word


def format_machine_names(df, column):
    turkish_char_dict = {"ı": "i", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "Ş": "s", "-": "_",
                         "ş": "s", "İ": "I", "Ö": "O", "ö": "o", "Ç": "C", "ç": "c", " ": "_", "/": "_"}
    machine_dict = {}
    for item in list(set(df[column])):
        machine_dict[item] = (format_word(item, turkish_char_dict))
    return df[column].replace(machine_dict)


def determine_amounts(df):
    copy_series = pd.Series(np.nan, index=df.index)
    idx = df.level.lt(df.level.shift(1, fill_value=2)) | df.level.eq(1)
    copy_series[idx] = df.loc[idx, "amount"]
    copy_series.ffill(inplace=True)
    return copy_series


def corrupt_product_bom(group):
    if (sum(group.level == 1) == 0) | (
            sum((group.level - group.level.shift(1, fill_value=group.at[group.index[0], "level"])) >= 2) != 0):
        return pd.DataFrame({"is_valid": [True] * len(group)}, index=group.index)
    else:
        return pd.DataFrame({"is_valid": [False] * len(group)}, index=group.index)


def find_most_close_products(missing_products, complete_df) -> dict:
    product_parameter = [10, 5, 3, 1]
    products = pd.DataFrame(complete_df.product_no.unique(), columns=["product_no"])
    products[["product_family", "length", "customer", "option"]] = products.product_no.str.split(".", expand=True)
    missing_prods = pd.DataFrame(missing_products.product_no.unique(), columns=["product_no"])
    missing_prods[["product_family", "length", "customer", "option"]] = missing_prods.product_no.str.split(".",
                                                                                                           expand=True)
    missing_dict = {missing_prods.product_no[x]:
                        products[::-1].product_no[
                            ((products[products.columns[-4:]] == missing_prods.iloc[x, -4:]) * product_parameter).sum(
                                axis=1).idxmax()] for x in
                    missing_prods.index}
    return missing_dict


# noinspection PyTypeChecker
def create_operational_table(df, table_type, aux=None, *args):
    if table_type == "legend":
        df = df.iloc[finder.input_indices(df)][["product_no", "part_no"]]
        df.index = list(range(1, len(df) + 1))
        return df
    elif table_type == "input":
        df = df.iloc[finder.input_indices(df)][["product_no", "amount"]]
        df["product_no"] = finder.product_numerator(df)
        df.index = list(range(1, len(df) + 1))
        df.columns = ["product", "amount"]
        return df
    elif table_type == "dup":
        # This function gets the input table as a base dataframe to work on and make calculations with.
        df = create_operational_table(df=df, table_type="input")

        # The following three lines creates the products' index in the process input list, i.e. from the input table
        s = df["product"].ne(df["product"].shift(fill_value=df.iloc[0]["product"]))
        product_idx = pd.Series([1] + list(np.where(s)[0] + 1))
        product_idx.index += 1

        # Following line calculates the entity amounts to be duplicated in the simulation software
        dup_count = product_idx.shift(-1, fill_value=len(df) + 1) - product_idx

        # The next two lines concatanates, basically zipps the created product index and the duplication amounts and
        # converts them to a pandas dataframe with the product # with them.
        duplication_table = pd.concat(
            [pd.Series(list(range(1, len(product_idx) + 1)), index=list(range(1, len(product_idx) + 1))), product_idx,
             dup_count], axis=1)
        duplication_table.columns = ["product", "start", "number to duplicate"]
        return duplication_table
    elif table_type == "sequence":
        df_copy = df.copy().reset_index()
        dummies = pd.get_dummies(df_copy["level"])

        lookup_series = df_copy["station"]
        gross_matrix = dummies.apply(lambda col: lookup_series.where(col != 0, np.nan).fillna(method="ffill"))
        gross_matrix.index = df.index

        gross_matrix = gross_seq_matrix_trimmer(gsm=gross_matrix, df=df, matrix_type="station")
        gross_matrix.index = list(range(1, gross_matrix.shape[0] + 1))
        return gross_matrix
    elif table_type == "time":
        df_copy = df.copy().reset_index()
        dummies = pd.get_dummies(df_copy["level"])

        lookup_series = df_copy["cycle_times"].copy()
        gross_matrix = dummies.apply(lambda col: lookup_series.where(col != 0, np.nan).fillna(method="ffill"))
        gross_matrix.index = df.index

        gross_matrix = gross_seq_matrix_trimmer(gsm=gross_matrix, df=df, matrix_type="time")
        gross_matrix.index = list(range(1, gross_matrix.shape[0] + 1))
        return gross_matrix
    elif table_type == "joins":
        # Tutorial df for joining matrix
        df = df[["product_no", "level"]].copy()
        df["product_no"] = finder.product_numerator(df)
        # df = df[df["product_no"].le(100)].copy()
        input_idx = finder.input_indices(df)
        join_df = df.loc[finder.joining_indices(df)].copy()
        join_matrix = pd.DataFrame(index=input_idx, columns=list(range(1, df.level.max() + 1)))
        join_idx = 2
        product_assembly_amount = df.loc[finder.input_indices(df)].copy().reset_index().groupby(by="product_no").agg(
            {"index": list, "level": list})
        product_assembly_amount["count"] = df.copy().reset_index().groupby(by="product_no").apply(num_of_input)
        join_amount_count = [1]
        # start loop here
        while len(join_df) > 0:
            curr_row = int(join_df.tail(1).index[0])
            curr_level = df.loc[curr_row, "level"]
            start_row = curr_row
            end_row = int(df[df["level"].eq(df.loc[curr_row, "level"] - 1) & (df.index < curr_row)].tail(1).index[0])
            middle_parts = df[
                df["level"].eq(df.loc[curr_row, "level"]) & (df.index <= start_row) & (df.index >= end_row)]
            inputs_n_levels = [[input_idx[input_idx >= x][0], df.loc[input_idx[input_idx >= x][0], "level"]] for x in
                               middle_parts.index]
            if pd.isna(join_matrix.loc[inputs_n_levels[0][0], inputs_n_levels[0][1] - curr_level + 1]):
                product_assembly_amount.loc[df.loc[inputs_n_levels[0][0], "product_no"], "count"] -= (
                        len(inputs_n_levels) - 1)
                for inputs in inputs_n_levels:
                    join_matrix.loc[inputs[0], inputs[1] - curr_level + 1] = join_idx
                join_df.drop(join_df.tail(1).index[0], inplace=True)
                join_amount_count.append(len(inputs_n_levels))
                join_idx += 1
            else:
                join_df.drop(join_df.tail(1).index[0], inplace=True)

        for product_idx in product_assembly_amount.index:
            temp_idx = product_assembly_amount.loc[product_idx, "index"]
            for idx in temp_idx:
                join_matrix.loc[idx, df.loc[idx, "level"]] = join_idx
                join_matrix.loc[idx, list(range(1, df.loc[idx, "level"]))] = \
                    join_matrix.loc[idx, list(range(1, df.loc[idx, "level"]))].fillna(1)
            join_amount_count.append(product_assembly_amount.loc[product_idx, "count"])
            join_idx += 1

        join_amount_df = pd.DataFrame(
            {"join_code": list(range(1, len(join_amount_count) + 1)), "amount": join_amount_count},
            index=list(range(1, len(join_amount_count) + 1)))
        join_matrix.reset_index(drop=True, inplace=True)
        join_matrix.index = list(range(1, join_matrix.shape[0] + 1))
        join_amount_df.amount[join_amount_df.amount < 1] = 1

        return join_matrix, join_amount_df
    elif table_type == "set_list":
        x_y_coord = pd.merge(left=df, right=aux, left_on="stations_list", right_on="machine", how="left").loc[:,
                    ["x_coordinate", "y_coordinate"]]
        df["queues_list"] = [str(x) + "_Q" for x in df.stations_list]
        df["resources_list"] = [str(x) + "_RES" for x in df.stations_list]
        df[["x_coordinates", "y_coordinates"]] = x_y_coord
        df = df[[df.columns[0]] + list(df.columns[3:]) + list(df.columns[1:3])]
        df.index = list(range(1, df.shape[0] + 1))
        return df
    elif table_type == "order":
        products = aux.copy()
        prod_idx = products["product_no"].ne(
            products["product_no"].shift(1, fill_value=products.iloc[0]["product_no"])).cumsum() + 1
        products["prod_code"] = prod_idx
        idx_dict = \
            products.drop_duplicates("product_no", keep="first").drop("part_no", axis=1).set_index("product_no",
                                                                                                   drop=True).to_dict()[
                "prod_code"]
        whole_dataframe = df.copy()
        whole_dataframe.product_no.replace(idx_dict, inplace=True)
        whole_dataframe["day_of_month"] = whole_dataframe.start_date.dt.day
        # whole_dataframe["day_of_month"] = [int(x.days) for x in whole_dataframe["day_of_month"]]
        # if sum(whole_dataframe.iloc[:int(whole_dataframe.shape[0]/2), :].reset_index(drop=True).start_date == whole_dataframe.iloc[int(whole_dataframe.shape[0]/2):, :].reset_index(drop=True).start_date)==int(whole_dataframe.shape[0]/2):
        if args[0] > 1:
            if args[1]:
                whole_dataframe.drop(whole_dataframe[~whole_dataframe["start_date"].dt.month ==
                                                     whole_dataframe["start_date"].dt.month.mode().values[0]].index,
                                     inplace=True)

                if whole_dataframe.start_date.dt.month.mode().values[0] != 12:
                    curr_month_day = (datetime(year=whole_dataframe.start_date.dt.year.mode().values[0],
                                               month=whole_dataframe.start_date.dt.month.mode().values[0] + 1,
                                               day=1) - pd.to_timedelta(1, unit="d")).day
                else:
                    curr_month_day = (datetime(year=whole_dataframe.start_date.dt.year.mode().values[0] + 1, month=1,
                                               day=1) - pd.to_timedelta(1, unit="d")).day

                whole_dataframe.loc[int(whole_dataframe.shape[0] / 2):, "day_of_month"] = [x + curr_month_day for x in
                                                                                           whole_dataframe.iloc[int(
                                                                                               whole_dataframe.shape[
                                                                                                   0] / 2):,
                                                                                           :].day_of_month]
                # This is VERY, VERY dumb
                whole_dataframe["due_date"] = pd.concat(
                    [whole_dataframe.loc[:int(whole_dataframe.shape[0] / 2) - 1, "due_date"],
                     whole_dataframe.loc[int(whole_dataframe.shape[0] / 2):, "due_date"] + pd.to_timedelta(
                         curr_month_day, unit="d")])
                whole_dataframe["start_date"] = pd.concat(
                    [whole_dataframe.loc[:int(whole_dataframe.shape[0] / 2) - 1, "start_date"],
                     whole_dataframe.loc[int(whole_dataframe.shape[0] / 2):, "start_date"] + pd.to_timedelta(
                         curr_month_day, unit="d")])
                # THIS LINE CAUSED REDUNDANCY AFTER MULTIPLE PLAN SPLIT, IS COMMENTED OUT FOR NOW
                # whole_dataframe.drop(whole_dataframe[whole_dataframe["day_of_month"] > curr_month_day*args[0]].index, inplace = True)
            else:
                months_count = whole_dataframe["start_date"].dt.month.value_counts().to_dict()
                plan_months = []
                for _ in range(len(months_count.keys())):
                    plan_months.append(max(months_count, key=lambda x: months_count[x]))
                    months_count.pop(max(months_count, key=lambda x: months_count[x]))
                whole_dataframe.drop(whole_dataframe[~whole_dataframe["start_date"].dt.month.isin(plan_months)].index,
                                     inplace=True)
                first_month_day = (datetime(whole_dataframe["start_date"].dt.year.max(),
                                            whole_dataframe["start_date"].dt.month.max(), 1) - pd.to_timedelta(1,
                                                                                                               unit="d")).day
                whole_dataframe.loc[whole_dataframe["start_date"].dt.month == max(plan_months), "day_of_month"] = \
                whole_dataframe.loc[
                    whole_dataframe["start_date"].dt.month == max(plan_months), "day_of_month"] + first_month_day
        else:
            whole_dataframe.drop(whole_dataframe[~whole_dataframe["start_date"].dt.month ==
                                                 whole_dataframe["start_date"].dt.month.mode().values[0]].index,
                                 inplace=True)

        whole_dataframe.reset_index(drop=True, inplace=True)
        whole_dataframe["sim_release_time"] = whole_dataframe.groupby("day_of_month").apply(
            create_sim_time_release_month)
        whole_dataframe["due_date_attribute"] = [x.strftime("%y%m%d") for x in whole_dataframe.due_date]
        whole_dataframe["days_until_due"] = [x.days for x in whole_dataframe.due_date - whole_dataframe.start_date]
        whole_dataframe = whole_dataframe[
            ["product_no", "sim_release_time", "amount", "due_date_attribute", "days_until_due"]].copy()
        whole_dataframe.sort_values("sim_release_time", inplace=True)
        whole_dataframe.index = list(range(1, whole_dataframe.shape[0] + 1))
        return whole_dataframe
    else:
        raise KeyError


def create_tactical_table(df, table_type):
    if table_type == "mult":
        df = df.copy()
        df.amount = df.amount.astype(int)
        df.cycle_times = df.cycle_times.astype(float)
        df.cycle_times = df.amount * df.cycle_times.astype(float)
        df.drop(finder.joining_indices(df), inplace=True)
        df.drop(df[df.product_no.eq(df.product_no.shift(1, fill_value=0)) & df.level.eq(1)].index, inplace=True)
        production_path = df.groupby("station", as_index=False).agg({"level": np.mean})
        production_path.sort_values("level", ascending=False, inplace=True)
        machine_legend_table = production_path["station"].copy()
        machine_legend_table.index = list(range(1, machine_legend_table.shape[0] + 1))
        machine_legend_table = machine_legend_table.to_frame()
        production_path.drop("level", axis=1, inplace=True)
        production_path.columns = [1]
        production_path = production_path.transpose()
        production_path.columns = list(range(1, production_path.shape[1] + 1))
        df = df.groupby(["product_no", "station"], as_index=False).agg({"cycle_times": sum})
        # mean_table = df.groupby(["product_no", "station"], as_index = False).agg({"cycle_times": sum})
        df["product_family"] = df.product_no.str.split(".").apply(lambda x: x[0])
        product_family_legend_table = pd.DataFrame(df.product_family.unique().tolist(), columns=["product_family"],
                                                   index=list(range(1, len(df.product_family.unique().tolist()) + 1)))
        count_dict = {x: df[df.product_family == x].product_no.nunique() for x in
                      df.product_family.unique()}
        prob_table = df.groupby(["product_family", "station"], as_index=False).agg({"product_no": "count"})
        prob_table["total_products"] = prob_table.product_family
        prob_table.total_products.replace(count_dict, inplace=True)
        prob_table["probabilities"] = prob_table.product_no / prob_table.total_products
        prob_table.drop(["product_no", "total_products"], axis=1, inplace=True)
        prob_table = prob_table.pivot("product_family", "station", "probabilities").fillna(0)
        prob_table = prob_table[list(production_path.to_numpy()[0])].copy()
        df = df.groupby(["product_family", "station"], as_index=False).agg({"cycle_times": [min, np.mean, max]})
        df.columns = ["product_family", "station", "min", "mean", "max"]
        min_table = df.pivot("product_family", "station", "min").fillna(0)
        min_table = min_table[list(production_path.to_numpy()[0])].copy()
        mean_table = df.pivot("product_family", "station", "mean").fillna(0)
        mean_table = mean_table[list(production_path.to_numpy()[0])].copy()
        max_table = df.pivot("product_family", "station", "max").fillna(0)
        max_table = max_table[list(production_path.to_numpy()[0])].copy()
        for table in [prob_table, min_table, mean_table, max_table]:
            table.index = list(range(1, table.shape[0] + 1))
            table.columns = list(range(1, table.shape[1] + 1))
        return product_family_legend_table, machine_legend_table, production_path, min_table, mean_table, max_table, prob_table
    elif table_type == "set_list":
        df["queues_list"] = [str(x) + "_Q" for x in df.stations_list]
        df["resources_list"] = [str(x) + "_RES" for x in df.stations_list]
        df["x_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
        df["y_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
        df = df[[df.columns[0]] + list(df.columns[3:]) + list(df.columns[1:3])]
        df.index = list(range(1, df.shape[0] + 1))
        return df
    elif table_type == "order":
        temp_df = df[df.columns[-12:]].copy()
        temp_df.reset_index(inplace=True)
        temp_df = temp_df.melt(id_vars="product_no")
        temp_df["date"] = pd.to_datetime(temp_df.date)
        temp_df["product_family"] = temp_df.product_no.str.split(".").apply(lambda x: x[0])
        temp_df.groupby(["product_family", "date"], as_index=False).agg({"value": sum})
        temp_df = temp_df.groupby(["product_family", "date"], as_index=False).agg({"value": sum})
        temp_df = temp_df.groupby(by=["product_family", "date"], as_index=False).apply(create_sim_timestamps)
        temp_df.drop(temp_df[temp_df.amount == 0].index, inplace=True)
        temp_df.reset_index(drop=True, inplace=True)
        products = temp_df.copy()
        prod_idx = products["product_family"].ne(
            products["product_family"].shift(1, fill_value=products.iloc[0]["product_family"])).cumsum() + 1
        products["prod_code"] = prod_idx
        idx_dict = \
            products.drop_duplicates("product_family", keep="first").set_index("product_family", drop=True).to_dict()[
                "prod_code"]
        temp_df.product_family.replace(idx_dict, inplace=True)
        temp_df["day_of_year"] = temp_df.start_date.dt.dayofyear
        temp_df["sim_release_time"] = temp_df.groupby("day_of_year").apply(create_sim_time_release_year)
        temp_df["due_date_attribute"] = [x.strftime("%y%m%d") for x in temp_df.due_date]
        temp_df["days_until_due"] = (temp_df.due_date - temp_df.start_date).dt.days
        temp_df = temp_df[
            ["product_family", "sim_release_time", "amount", "due_date_attribute", "days_until_due"]].copy()
        temp_df.sort_values("sim_release_time", inplace=True)
        temp_df.reset_index(drop=True, inplace=True)
        return temp_df
    elif table_type == "set_list":
        df = df.copy()
        df["queues_list"] = [str(x) + "_Q" for x in df.stations_list]
        df["resources_list"] = [str(x) + "_RES" for x in df.stations_list]
        df["x_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
        df["y_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
        df = df[[df.columns[0]] + list(df.columns[3:]) + list(df.columns[1:3])]
        df.index = list(range(1, df.shape[0] + 1))
        return df
    else:
        raise KeyError


def gross_seq_matrix_trimmer(gsm, df, matrix_type):
    max_level = df.level.max()
    input_idx = finder.input_indices(df)
    temp_df = df.loc[input_idx]
    trimmed_df = None
    if matrix_type == "station":
        trimmed_df = pd.DataFrame(index=input_idx, columns=list(range(1, gsm.columns.max() + 2)))
        for curr_level in range(max_level, 1, -1):
            temp_idx = temp_df.loc[temp_df.level == curr_level].index
            temp_seq = gsm.loc[temp_idx][list(range(curr_level, 0, -1))]
            temp_seq[curr_level + 1] = "ENDING_STATION"
            temp_seq.columns = list(range(1, curr_level + 2))
            trimmed_df.loc[temp_idx, list(range(1, curr_level + 2))] = temp_seq
    elif matrix_type == "time":
        trimmed_df = pd.DataFrame(index=input_idx, columns=list(range(1, gsm.columns.max() + 1)))
        for curr_level in range(max_level, 1, -1):
            temp_idx = temp_df.loc[temp_df.level == curr_level].index
            temp_seq = gsm.loc[temp_idx][list(range(curr_level, 0, -1))]
            temp_seq.columns = list(range(1, curr_level + 1))
            trimmed_df.loc[temp_idx, list(range(1, curr_level + 1))] = temp_seq
    trimmed_df.reset_index(drop=True, inplace=True)
    return trimmed_df


def num_of_input(group):
    return len(finder.input_indices(group))


def create_sim_time_release_month(group):
    temp = group["day_of_month"] * 60 * 60 * 24
    # noinspection PyTypeChecker
    temp = temp + list(range(len(temp)))
    return pd.DataFrame(temp, index=group.index)


def create_sim_time_release_year(group):
    temp = group["day_of_year"] * 60 * 60 * 24
    # noinspection PyTypeChecker
    temp = temp + list(range(len(temp)))
    return pd.DataFrame(temp, index=group.index)


def check_input_validity(group):
    if len(group.level.unique()) == group.level.max():
        return pd.DataFrame([True] * len(group), index=group.index)
    else:
        return pd.DataFrame([False] * len(group), index=group.index)


def create_input_branches(group):
    new_series = group.groupby(by=group.level.eq(1).cumsum()).apply(check_input_validity)
    return pd.DataFrame(new_series, index=group.index)


def create_sim_timestamps(group):
    if group.value == 0:
        return pd.DataFrame(columns=["product_family", "amount", "start_date", "due_date"])
    else:
        length_multiplier = int(np.select(
            [group.value <= 10, group.value <= 50, group.value <= 250, group.value <= 500, group.value > 500],
            [1, 2, 4, 6, 8]))
        rel = relativedelta(days=int(30 / length_multiplier))
        start_dates = group.date.apply(lambda x: [x + y * rel for y in range(length_multiplier)])[0]
        end_dates = \
        group.date.apply(lambda x: [x + y * rel - relativedelta(days=1) for y in range(1, length_multiplier + 1)])[0]
        return pd.DataFrame({"product_family": [group.product_family.values[0]] * length_multiplier,
                             "amount": [int(group.value / length_multiplier)] * length_multiplier,
                             "start_date": start_dates, "due_date": end_dates})


def ctesi_creator(hour):
    if hour < 24:
        out = pd.DataFrame(data=[[1, hour], [0, 24 - hour]])
    else:
        out = pd.DataFrame(data=[[1, 24], [0, 0]])
    return out


def weekday_creator(shift, overtime_per_day):
    if shift == 1:
        if overtime_per_day == 0:
            return pd.DataFrame(data=[[1, 0, 0, 0, 0, 0], [7.5, 0.5] * 3]).transpose()
        elif overtime_per_day < 7.5:
            return pd.DataFrame(data=[[1, 0, 1, 0, 0, 0],
                                      [7.5, 0.5, overtime_per_day, 0.5 + (7.5 - overtime_per_day), 7.5,
                                       0.5]]).transpose()
        elif overtime_per_day < 15:
            return pd.DataFrame(data=[[1, 0, 1, 0, 1, 0], [7.5, 0.5] + [(overtime_per_day / 2), 0.5 + (
                        7.5 - (overtime_per_day / 2))] * 2]).transpose()
        else:
            return pd.DataFrame(data=[[1, 0, 1, 0, 1, 0], [7.5, 0.5] * 3]).transpose()
    if shift == 2:
        if overtime_per_day == 0:
            return pd.DataFrame(data=[[1, 0, 1, 0, 0, 0], [7.5, 0.5] * 3]).transpose()
        elif overtime_per_day < 7.5:
            return pd.DataFrame(data=[[1, 0, 1, 0, 1, 0],
                                      [7.5, 0.5] * 2 + [overtime_per_day, 0.5 + (7.5 - overtime_per_day)]]).transpose()
        else:
            return pd.DataFrame(data=[[1, 0, 1, 0, 1, 0], [7.5, 0.5] * 3]).transpose()
    elif shift == 3:
        return pd.DataFrame(data=[[1, 0, 1, 0, 1, 0], [7.5, 0.5] * 3]).transpose()


def outsource_creator(outsource_amount):
    if outsource_amount < 24:
        return pd.DataFrame(data=[[1, 0], [outsource_amount, 24 - outsource_amount]]).transpose()
    else:
        return pd.DataFrame(data=[[1, 0], [24, 0]]).transpose()

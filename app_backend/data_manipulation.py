import pandas as pd
import numpy as np
import app_backend.finder as finder
from app_backend.excel_operations import read_excel_sheet
from random import randint


"""
######################
#       Initial      #         
#      edits of      #
#     dataframes     #
######################
"""


def arrange_df(df, df_type, relevant_col_idx=None, tbd_path="no_dir", assembly_df=None):  # , cmy_df=None
    """
    :param df:
    pandas.DataFrame object that contains the raw format that is read from the file.
    :param df_type:
    File type of
    :param relevant_col_idx:
    :param tbd_path:
    :param assembly_df:
    :return:
    """
    if df_type.lower() == "bom":
        # Reformatting the columns
        df = reformat_columns(df, relevant_col_idx, "bom")

        # Deleting the trial products
        df.drop(df[df.product_no.apply(lambda x: int(x.split(".")[2]) >= 900)].index, inplace = True)
        df.reset_index(drop="index", inplace=True)

        # This to be deleted parts can be redundant, so it will be decided that if these codes are going to stay or not
        items_to_delete = read_excel_sheet(tbd_path)
        s = [str(x).split(".")[0] not in list(items_to_delete["Kalacaklar"]) for x in df["part_no"]]
        df = df.drop(np.where(np.asarray(s))[0])

        # Deleting the entries where two successive entries are level 1s.
        s = (df[df.columns[2]].ne(df[df.columns[2]].shift(1, fill_value = 1)) | df[df.columns[2]].ne(1)).cumsum()
        df = df.groupby(s).tail(1)

        # This is the part where the deletion occurs if the last column's level is 1.
        if df.at[df.index[-1], df.columns[2]] == 1:
            df.drop(df.index[-1], inplace = True)

        # Making sure that the dataframe returns in order
        df.reset_index(drop = "index", inplace = True)

        # This part is not certain
        df["product_family"] = [x.split(".")[0] for x in df.product_no]
        first_products = df[df.product_family.ne(df.product_family.shift(1, fill_value = 0))]["product_no"].to_list()
        a = pd.Series([x in first_products for x in df.product_no])
        df.drop(df[~a].index, inplace = True)
        df.reset_index(drop = "index", inplace = True)

        return df

    if df_type.lower() == "times":
        # Reformatting the columns
        df = reformat_columns(df, relevant_col_idx, "times")

        # Transforming the machine names to ASCII characters.
        df["station"] = format_machine_names(df, "station")
        set_list_df = pd.DataFrame({"stations_list": list(set(df.station.to_list()))})

        # Creating a dataframe with the assembly times
        montaj_df = df[(df["station"] == "BANT") | (df["station"] == "LOOP")]

        # Creating a dataframe with the glass bonding
        cmy_df = df[df["station"] == "CAM_YAPISTIRMA"]

        # Dropping the assembly times from the original times dataframe and resetting the index
        df.drop(df[(df["station"] == "BANT") |
                   (df["station"] == "LOOP") |
                   (df["station"] == "CAM_YAPISTIRMA") |
                   (df["part_no"].apply(lambda x: len(x)) == 13)].index, inplace = True)

        # Grouping by the times of the parts that has multiple times in the same work station
        df = df.groupby(["part_no", "station"], as_index = False).agg({"cycle_times": sum, "prep_times": max})
        df.drop(df[df["part_no"].duplicated(keep = "last")].index, inplace = True)

        # Filling the NA codes with 0s (0 codes come from the items that have no time info)
        df[["prep_times", "cycle_times"]] = df[["prep_times", "cycle_times"]].fillna(0)

        # Resetting the index
        df.reset_index(drop = "index", inplace = True)

        return df, montaj_df, cmy_df, set_list_df

    if df_type.lower() == "merged":
        df["station"] = level_lookup(df, "level", "station")
        df["cycle_times"] = level_lookup(df, "level", "cycle_times")
        df["prep_times"] = level_lookup(df, "level", "prep_times")

        df.loc[df.level == 1, ["station", "cycle_times", "prep_times"]] = \
            pd.merge(df["product_no"], assembly_df[["part_no", "station", "cycle_times", "prep_times"]], "left",
                     left_on = "product_no",
                     right_on = "part_no")[["station", "cycle_times", "prep_times"]]

        missing_dict = missing_values_df(df)
        missing_df = pd.DataFrame(missing_dict).transpose().reset_index()
        missing_df.columns = ["code", "station", "cycle_times", "prep_times"]
        # Ask for what are the values for the NAs in the missing dictionary
        """
        THIS WILL CHANGE
        """
        missing_df.station.fillna("CAM_YAPISTIRMA", inplace = True)
        missing_df.cycle_times.fillna(45, inplace = True)
        missing_df.prep_times.fillna(0, inplace = True)
        """
        END OF THIS WILL CHANGE
        """
        # Rounding all the numerical values to integers.
        missing_df.loc[~missing_df.station.isna(), ["cycle_times", "prep_times"]] = \
            missing_df.loc[~missing_df.station.isna()][["cycle_times", "prep_times"]].apply(np.ceil)

        # Creating the missing slice to fill it to the merged bom dataframe later
        missing_slice = pd.merge(left = df.part_no.apply(lambda x: x.split(".")[0]).loc[df.station.isna()],
                                 right = missing_df, left_on = "part_no", right_on = "code", how = "left")
        missing_slice.index = df.loc[df.station.isna()].index

        # Equating the filled missing data slice into the bom
        df.loc[df.station.isna(), ["station", "cycle_times", "prep_times"]] = \
            missing_slice[["station", "cycle_times", "prep_times"]]

        return df


def reformat_columns(df, relevant_col_idx, df_type):
    if df_type == "bom":
        # Rearranging the level amount
        df["Seviye"] = [int(x[-1]) for x in df[df.columns[relevant_col_idx][2]]]
        relevant_col_idx[2] = len(df.columns) - 1

        # Determining the columns names to use for reindex later
        relevant_col_names = df.columns[relevant_col_idx]

        # Columns to be dropped from the dataframe
        cols_to_drop = list(set(df.columns) - set(df.columns[relevant_col_idx]))

        # Dropping, sorting and indexing the corresponding columns
        df.drop(cols_to_drop, axis = 1, inplace = True)
        df = df.reindex(columns = relevant_col_names)
        df.columns = ["product_no", "part_no", "level", "amount", "explanation"]

    if df_type == "times":
        # Determining the columns names to use for reindex later
        relevant_col_names = df.columns[relevant_col_idx]

        # Columns to be dropped from the dataframe
        cols_to_drop = list(set(df.columns) - set(df.columns[relevant_col_idx]))

        # Dropping, sorting and indexing the corresponding columns
        df.drop(cols_to_drop, axis = 1, inplace = True)
        df = df.reindex(columns = relevant_col_names)
        df.columns = ["part_no", "station", "cycle_times", "prep_times"]

    return df


"""
######################
#       Tools        #         
#         of         #
#    manipulation    #
######################
"""


def level_lookup(df, level_col, lookup_col):
    dummies = pd.get_dummies(df[level_col])

    idx = dummies.index.to_series()
    last_index = dummies.apply(lambda col: idx.where(col != 0, np.nan).fillna(method = "ffill"))
    last_index[0] = 1

    idx = last_index.lookup(last_index.index, df[level_col] - 1)
    return pd.DataFrame({lookup_col: df.reindex(idx)[lookup_col].values}, index = df.index)


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
            temp_seq.columns = list(range(1, curr_level+2))
            trimmed_df.loc[temp_idx, list(range(1, curr_level+2))] = temp_seq
    elif matrix_type == "time":
        trimmed_df = pd.DataFrame(index=input_idx, columns=list(range(1, gsm.columns.max() + 1)))
        for curr_level in range(max_level, 1, -1):
            temp_idx = temp_df.loc[temp_df.level == curr_level].index
            temp_seq = gsm.loc[temp_idx][list(range(curr_level, 0, -1))]
            temp_seq.columns = list(range(1, curr_level+1))
            trimmed_df.loc[temp_idx, list(range(1, curr_level+1))] = temp_seq
    trimmed_df.reset_index(drop = "index", inplace = True)
    return trimmed_df


def missing_values_df(df):
    missing_parts = df[df.station.isna()].part_no.apply(lambda x: x.split(".")[0]).unique()
    missing_dict = {}
    for items in missing_parts:
        temp_station = df[df.part_no.apply(lambda x: x.split(".")[0]) == items].station.mode()
        if temp_station.shape == (0,):
            temp_station = np.nan
        else:
            temp_station = temp_station[0]
        temp_cycle = df[df.part_no.apply(lambda x: x.split(".")[0]) == items].cycle_times.mean()
        temp_prep = df[df.part_no.apply(lambda x: x.split(".")[0]) == items].prep_times.mean()
        missing_dict[items] = [temp_station, temp_cycle, temp_prep]
    return missing_dict


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
    return [machine_dict[x] for x in df[column]]


def merge_bom_and_times(df_bom, df_times):
    merged_df = pd.merge(left = df_bom, right = df_times, how = "left", on = "part_no")
    merged_df = merged_df.reindex(
        columns = list(merged_df.columns[0:4]) + list(merged_df.columns[5:]) + list(merged_df.columns[4:5]))
    return merged_df


def determine_amounts(df):
    df["new_amount"] = 1
    bom_row = 0
    while bom_row < len(df):
        if (df.loc[bom_row, "amount"] % 1 == 0) and (df.loc[bom_row, "amount"] != 1):
            starting_amount = df.loc[bom_row, "amount"]
            df.loc[bom_row, "new_amount"] = starting_amount
            starting_level = df.loc[bom_row, "level"]
            while bom_row < len(df):
                bom_row += 1
                if df.at[bom_row, "level"] > starting_level:
                    df.at[bom_row, "new_amount"] = starting_amount
                else:
                    break
        bom_row += 1
    df['amount'] = df['new_amount']
    df.drop('new_amount', axis = 1, inplace = True)
    df.reset_index(drop = "index", inplace = True)
    return df


"""
######################
#       Output       #         
#      dataframe     #
#      creators      #
######################
"""


def create_legend_table(df):
    df = df.iloc[finder.input_indices(df)][["product_no", "part_no"]]
    df.index = list(range(1, len(df) + 1))
    return df


def create_input_table(df):
    df = df.iloc[finder.input_indices(df)][["product_no", "amount"]]
    df["product_no"] = finder.product_numerator(df)
    df.index = list(range(1, len(df) + 1))
    df.columns = ["product", "amount"]
    return df


def sequence_type_matrix(df, lookup_col, matrix_type):
    df_copy = df.copy().reset_index()
    dummies = pd.get_dummies(df_copy["level"])

    lookup_series = df_copy[lookup_col]
    gross_matrix = dummies.apply(lambda col: lookup_series.where(col != 0, np.nan).fillna(method = "ffill"))
    gross_matrix.index = df.index

    gross_matrix = gross_seq_matrix_trimmer(gsm = gross_matrix, df = df, matrix_type = matrix_type)
    return gross_matrix


def create_join_matrix(df):
    # Tutorial df for joining matrix
    df = df[["product_no", "level"]].copy()
    df["product_no"] = finder.product_numerator(df)
    # df = df[df["product_no"].le(100)].copy()
    input_idx = finder.input_indices(df)
    join_df = df.loc[finder.joining_indices(df)].copy()
    join_matrix = pd.DataFrame(index = input_idx, columns = list(range(1, df.level.max() + 1)))
    join_idx = 2
    product_assembly_amount = df.loc[finder.input_indices(df)].copy().reset_index().groupby(by = "product_no").agg(
        {"index": list, "level": list})
    product_assembly_amount["count"] = [len(x) for x in product_assembly_amount["level"]]
    join_amount_count = [1]
    # start loop here
    while len(join_df) > 0:
        curr_row = int(join_df.tail(1).index[0])
        curr_level = df.loc[curr_row, "level"]
        start_row = curr_row
        end_row = int(df[df["level"].eq(df.loc[curr_row, "level"] - 1) & (df.index < curr_row)].tail(1).index[0])
        middle_parts = df[df["level"].eq(df.loc[curr_row, "level"]) & (df.index <= start_row) & (df.index >= end_row)]
        inputs_n_levels = [[input_idx[input_idx >= x][0], df.loc[input_idx[input_idx >= x][0], "level"]] for x in
                           middle_parts.index]
        if pd.isna(join_matrix.loc[inputs_n_levels[0][0], inputs_n_levels[0][1] - curr_level + 1]):
            product_assembly_amount.loc[df.loc[inputs_n_levels[0][0], "product_no"], "count"] -= (
                        len(inputs_n_levels) - 1)
            for inputs in inputs_n_levels:
                join_matrix.loc[inputs[0], inputs[1] - curr_level + 1] = join_idx
            join_df.drop(join_df.tail(1).index[0], inplace = True)
            join_amount_count.append(len(inputs_n_levels))
            join_idx += 1
        else:
            join_df.drop(join_df.tail(1).index[0], inplace = True)

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
        index = list(range(1, len(join_amount_count) + 1)))
    join_matrix.reset_index(drop = True, inplace = True)
    join_matrix.index = list(range(1, join_matrix.shape[0] + 1))

    return join_matrix, join_amount_df


def create_duplication_table(df):
    # This function gets the input table as a base dataframe to work on and make calculations with.
    df = create_input_table(df)

    # The following three lines creates the products' index in the process input list, i.e. from the input table
    s = df["product"].ne(df["product"].shift(fill_value = df.iloc[0]["product"]))
    product_idx = pd.Series([1] + list(np.where(s)[0] + 1))
    product_idx.index += 1

    # Following line calculates the entity amounts to be duplicated in the simulation software
    dup_count = product_idx.shift(-1, fill_value = len(df) + 1) - product_idx

    # The next two lines concatanates, basically zipps the created product index and the duplication amounts and
    # converts them to a pandas dataframe with the product # with them.
    duplication_table = pd.concat(
        [pd.Series(list(range(1, len(product_idx) + 1)), index = list(range(1, len(product_idx) + 1))), product_idx,
         dup_count], axis = 1)
    duplication_table.columns = ["product", "start", "number to duplicate"]
    return duplication_table


def set_list_table(df):
    df["queues_list"] = [str(x) + "_Q" for x in df.stations_list]
    df["resources_list"] = [str(x) + "_RES" for x in df.stations_list]
    df["x_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
    df["y_coordinates"] = [randint(-50, 150) for _ in df.stations_list]
    return df


def order_table(input_df, amount=10):
    max_product_idx = input_df["product"].max()
    order_df = pd.DataFrame({"product": [randint(1, max_product_idx) for _ in range(amount)],
                             "order_time": np.linspace(100, 8000, amount),
                             "order_size": [randint(1, 50) for _ in range(amount)]
                             }, index=range(1, amount+1))
    return order_df

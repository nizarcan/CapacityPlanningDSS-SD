from app_backend.utils.df_ops import arrange_df, merge_bom_and_times, trim_df, create_operational_table, \
    create_tactical_table, trim_order, format_machine_names, schedule_changer_dict, ctesi_creator
from app_backend.utils.xl_ops import load_file, load_plan, add_plan, create_xl_file
import pandas as pd
from pandas import DataFrame, concat, merge, to_timedelta, to_datetime, read_excel
from app_backend.utils.demand_util import OrderHistory, extract_forecast
from app_backend.utils.finder import joining_indices
from datetime import datetime
import pickle


def revert_checkpoint(file_dir):
    with open(file_dir, "rb") as f:
        mdl = pickle.load(f)
        return mdl


class ArchiveDatabase:
    def __init__(self):
        self.bom_file = None
        self.times_file = None
        self.files_to_be_deleted = None
        self.order_history = OrderHistory()
        self.merged_file = None
        self.assembly_df = None
        self.cmy_df = None
        self.temp = None
        self.machine_info = None
        self.last_adition_date = datetime.now().date()

    def __repr__(self):
        if self.last_adition_date is None:
            return "An input file struct that holds the data but hasn't yet compiled and created a backup."
        else:
            return f"An input file struct that holds the data that is compiled at {self.last_adition_date}."

    def reassign_time(self):
        self.last_adition_date = datetime.now().date()

    def save_checkpoint(self, file_dir):
        with open(file_dir, "wb") as f:
            pickle.dump(self, f)

    def load_files_to_be_deleted(self, file_dir):
        self.files_to_be_deleted = load_file(file_dir)

    def load_bom(self, file_dir):
        self.bom_file = load_file(file_dir)
        self.bom_file = arrange_df(self.bom_file, "bom", [0, 3, 2, 5, 4], self.files_to_be_deleted)

    def load_times(self, file_dir):
        self.times_file = load_file(file_dir)
        self.times_file, self.assembly_df, self.cmy_df, self.temp = \
            arrange_df(self.times_file, "times", relevant_col_idx = [3, 25, 29, 28])

    def initialize_order_history(self):
        self.order_history.initialize()

    def load_machine_info(self, file_dir):
        self.machine_info = load_file(file_dir)

    def merge_files(self):
        self.merged_file = merge_bom_and_times(self.bom_file, self.times_file)
        self.merged_file = arrange_df(self.merged_file, "merged", assembly_df = self.assembly_df)


class OperationalSMInput:
    def __init__(self, parent_obj):
        # Parent attributes
        self.bom_file = parent_obj.bom_file
        self.times_file = parent_obj.times_file
        self.merged_file = parent_obj.merged_file
        self.temp = parent_obj.temp
        self.machine_info = parent_obj.machine_info
        # Input files attributes
        self.legend_table = None
        self.input_table = None
        self.duplication_matrix = None
        self.sequence_matrix = None
        self.time_matrix = None
        self.join_matrix = None
        self.join_amount_table = None
        self.set_list_table = None
        self.order_table = None
        self.plan_count = 0
        self.schedules = None
        self.math_model_output = {}
        self.days = {}
        # Plan init
        self.plan = None
        self.schedules = {}
        self.is_duplicate = False

    def load_math_model_output(self, file_dir):
        self.math_model_output["machine_legend"] = pd.read_excel(file_dir, sheet_name="machine_legend", index_col=0)
        self.math_model_output["overtime"] = pd.read_excel(file_dir, sheet_name="A")
        self.math_model_output["overtime"] = self.math_model_output["overtime"][self.math_model_output["overtime"][self.math_model_output["overtime"].columns[0]] == 2].iloc[:, 1:]
        self.math_model_output["overtime"].set_index(keys=self.math_model_output["overtime"].columns[0], inplace=True)
        self.math_model_output["overtime"] = self.math_model_output["overtime"].sum(axis = 1)
        self.math_model_output["combo"] = pd.concat([self.math_model_output["machine_legend"], self.math_model_output["overtime"]], axis=1).fillna(0)

    def load_plan(self, file_dir):
        if not bool(self.plan_count):
            self.plan = load_plan(file_dir)
        else:
            self.plan, self.is_duplicate = add_plan(self.plan, file_dir)
        self.plan_count += 1

    def load_days(self, file_dir):
        days_df = read_excel(file_dir, header = 0, index_col = 0)
        self.days[str(days_df.index.values[0])] = days_df

    def trim_bom(self):
        self.merged_file, missing_dict = trim_df(self.merged_file, self.plan)
        self.plan.product_no.replace(missing_dict, inplace = True)

    def create_tables(self):
        self.trim_bom()
        self.schedules = self.create_schedules()
        self.legend_table = create_operational_table(self.merged_file, "legend")
        self.input_table = create_operational_table(self.merged_file, "input")
        self.duplication_matrix = create_operational_table(self.merged_file, "dup")
        self.sequence_matrix = create_operational_table(self.merged_file, "sequence")
        self.time_matrix = create_operational_table(self.merged_file, "time")
        self.join_matrix, self.join_amount_table = create_operational_table(self.merged_file, "joins")
        self.set_list_table = create_operational_table(self.temp, "set_list", aux = self.machine_info)
        self.order_table = create_operational_table(self.plan, "order", self.merged_file, self.plan_count, self.is_duplicate)

    def create_schedules(self):
        schedules = {}
        availability = {}

        for month in list(self.days.keys()):
            month_and_day = month.split(".")
            current_month = datetime(int(month_and_day[0]), int(month_and_day[1]), 1)
            end_day = [datetime(int(month_and_day[0]), int(month_and_day[1])+1, 1) - pd.to_timedelta(1, unit="d") if int(month_and_day[1]) < 12 else 31 for _ in range(1)][0].day
            availability[month] = [1 if (((current_month+pd.to_timedelta(x, unit="d")).weekday() < 5) and (self.days[month].values[0][x] == 1)) else 2 if (((current_month+pd.to_timedelta(x, unit="d")).weekday()==5) and (self.days[month].values[0][x]==1)) else 3 for x in range(end_day)]

        if self.plan_count==2:
            if self.is_duplicate:
                total_availability = availability[list(availability.keys())[0]]*2
            else:
                total_availability = availability[min(list(availability.keys()))] + availability[max(list(availability.keys()))]
        else:
            total_availability = availability[list(availability.keys())[0]]

        df_types = {1: {1: pd.DataFrame(data = [[1, 0, 0, 0, 0, 0], [7.5, 0.5]*3]).transpose(),
                        2: pd.DataFrame(data = [[1, 0, 1, 0, 0, 0], [7.5, 0.5]*3]).transpose(),
                        3: pd.DataFrame(data = [[1, 0, 1, 0, 1, 0], [7.5, 0.5]*3]).transpose()},
                    2: ctesi_creator,
                    3: pd.DataFrame(data = [0, 24]).transpose()}

        for machine in self.temp.stations_list.values:
            if machine in self.math_model_output["machine_legend"].values:
                overtime = self.math_model_output["combo"].loc[self.math_model_output["combo"]["station"]==machine, 0].values[0]/total_availability.count(2)
                shift = self.machine_info.loc[self.machine_info.machine == machine, "shift"].values[0]
                # THIS WILL BE REPLACED WITH COMBO DF
                quantity = self.machine_info.loc[self.machine_info.machine == machine, "quantity"].values[0]

                schedule = pd.concat([
                    df_types[1][shift] if x==1
                    else df_types[2](overtime) if x==2
                    else df_types[3] for x in total_availability], ignore_index=True)

                schedule[schedule.columns[0]] = schedule[schedule.columns[0]]*quantity
                schedules[machine] = schedule
            elif machine in self.machine_info["machine"].values:
                overtime = 0
                shift = self.machine_info.loc[self.machine_info.machine == machine, "shift"].values[0]
                # THIS WILL BE REPLACED WITH COMBO DF
                quantity = self.machine_info.loc[self.machine_info.machine == machine, "quantity"].values[0]
                schedule = pd.concat([
                    df_types[1][shift] if x==1
                    else df_types[2](overtime) if x==2
                    else df_types[3] for x in total_availability], ignore_index=True)
                schedule[schedule.columns[0]] = schedule[schedule.columns[0]]*quantity
                schedules[machine] = schedule
            else:
                overtime = 0
                shift = 1
                # THIS WILL BE REPLACED WITH COMBO DF
                quantity = 1
                schedule = pd.concat([
                    df_types[1][shift] if x==1
                    else df_types[2](overtime) if x==2
                    else df_types[3] for x in total_availability], ignore_index=True)
                schedule[schedule.columns[0]] = schedule[schedule.columns[0]]*quantity
                schedules[machine] = schedule

        return schedules

    def create_file(self, file_dir):
        create_xl_file(self, file_dir, "operational_simulation_model")


# Discontinued
class TacticalSMInput:
    def __init__(self, parent_obj):
        # Input files attributes
        self.merged_file = parent_obj.merged_file
        self.order_history = trim_order(parent_obj.order_history, self.merged_file).copy()
        self.temp = parent_obj.temp
        self.prod_family_legend_table = None
        self.machine_legend_table = None
        self.sequence_list = None
        self.min_matrix = None
        self.mean_matrix = None
        self.max_matrix = None
        self.prob_matrix = None
        self.set_list_table = None
        self.order_table = None

    def create_tables(self):
        self.prod_family_legend_table, self.machine_legend_table, self.sequence_list, self.min_matrix, self.mean_matrix, self.max_matrix, self.prob_matrix = create_tactical_table(
            self.merged_file, table_type = "mult")
        self.set_list_table = create_tactical_table(self.temp, "set_list")
        self.order_table = create_tactical_table(self.order_history, "order")

    def create_file(self, file_dir):
        create_xl_file(self, file_dir, "tactical_simulation_model")


class OperationalMMInput:
    def __init__(self, parent, file_dir):
        self.merged_file = parent.merged_file
        self.plan = load_plan(file_dir)
        self.machine_info = parent.machine_info
        self.order_history = parent.order_history
        self.setup = parent.temp
        self.cross_trim()
        self.product_no_legend = None
        self.machine_legend = None
        self.times = None
        self.route_prob = None
        self.machine_cnt = None
        self.shift = None
        self.cost = None
        self.order_averages = None
        self.days = None
        self.setup_time = None
        self.outsource_perm = None

    def cross_trim(self):
        self.plan = self.plan[self.plan.product_no.isin(self.merged_file.product_no)].copy()
        self.merged_file.drop(self.merged_file[~self.merged_file.product_no.isin(self.plan.product_no)].index,
                              inplace = True)
        self.merged_file.reset_index(inplace = True, drop = True)
        self.plan.reset_index(inplace = True, drop = True)

    def load_days(self, file_dir):
        self.days = read_excel(file_dir, header = 0, index_col = 0)

    def pivot_days(self):
        # df = self.plan.copy()
        # resch_dict = schedule_changer_dict(self.plan, self.days)
        # df.start_date = df.start_date.dt.date
        # df.start_date.replace(resch_dict, inplace = True)
        # df = df.groupby(by = ["product_no", "start_date"], as_index = False).agg({"amount": "sum"})
        # df["new_day"] = to_datetime(df.start_date).dt.day
        # # df["new_day"] = df["new_day"].apply(lambda x: x.days + 1)
        # last_day = [datetime(to_datetime(df.start_date).dt.year.mode()[0], to_datetime(df.start_date).dt.month.mode()[0] + 1, 1) -
        #             to_timedelta(1, unit = "d") if (to_datetime(df.start_date).dt.month.mode()[0] != 12)
        #             else datetime(to_datetime(df.start_date).dt.year.mode()[0] + 1, 1, 1) - to_timedelta(1, unit = "d") for _ in range(1)][0]
        # df = df.groupby(by=["product_no", "new_day"], as_index=False).agg({"amount": "sum"})
        # df = df.pivot("product_no", "new_day", "amount").fillna(0)
        # out_df = DataFrame(index = df.index, columns = list(range(1, last_day.day+1))).fillna(0)
        # out_df[df.columns] = df
        df = self.plan.copy()
        resch_dict = schedule_changer_dict(self.plan, self.days)
        df.start_date = df.start_date.dt.date
        df.start_date.replace(resch_dict, inplace = True)
        df = df.groupby(by = ["product_no", "start_date"], as_index = False).agg({"amount": "sum"})
        df["new_day"] = to_datetime(df.start_date).dt.day
        df = df.groupby(by = ["product_no", "new_day"], as_index = False).agg({"amount": "sum"})
        df = df.pivot("product_no", "new_day", "amount").fillna(0)
        workdays = list(set(resch_dict.values()))
        workdays.sort()
        out_df = DataFrame(index = df.index, columns = [to_datetime(x).day for x in workdays]).fillna(0)
        out_df[df.columns] = df
        out_df.columns = list(range(1, out_df.shape[1]+1))
        # df["new_day"] = df["new_day"].apply(lambda x: x.days + 1)
        return out_df

    def update_machine_info(self, file_dir):
        df = load_file(file_dir)
        df[df.columns[0]] = format_machine_names(df, df.columns[0])
        df = concat([self.machine_info[~self.machine_info["machine"].isin(df[df.columns[0]].to_list())], df])
        df.reset_index(inplace = True, drop = True)
        self.machine_info = df.copy()

    def create_tables(self, pivot=True):
        self.cross_trim()
        # df => merged_file
        df = self.merged_file.copy()
        df.amount = df.amount.astype(int)
        df.cycle_times = df.cycle_times.astype(float)
        df.cycle_times = df.amount*df.cycle_times.astype(float)
        df.drop(joining_indices(df), inplace = True)
        df.drop(df[df.product_no.eq(df.product_no.shift(1, fill_value = 0)) & df.level.eq(1)].index, inplace = True)

        # Legends for the machine route and the product number index
        production_path = df.groupby("station", as_index = False).agg({"level": "mean"})
        production_path.sort_values("level", ascending = False, inplace = True)
        machine_legend = production_path["station"].copy()
        machine_legend.index = list(range(1, machine_legend.shape[0] + 1))
        machine_legend = machine_legend.to_frame()
        production_path.drop("level", axis = 1, inplace = True)
        production_path.columns = [1]
        production_path = production_path.transpose()
        production_path.columns = list(range(1, production_path.shape[1] + 1))
        product_no_legend = DataFrame(df.product_no.unique().tolist(), index=list(range(1, df.product_no.nunique()+1)), columns = ["product_no"])
        machine_info_df = merge(left = machine_legend, right = self.machine_info, how = "left", left_on = "station",
                                right_on = "machine").fillna(1).iloc[:, [0, 2, 3]]
        machine_info_df.index = list(range(1, machine_info_df.shape[0] + 1))

        # AVERAGE ORDER SIZE
        avg_df = self.order_history.orders.groupby("product_no", as_index = False).agg({"date": "count", "amount": "sum"})
        avg_df["order_amount"] = avg_df.amount/avg_df.date
        avg_df.order_amount = avg_df.order_amount.floordiv(1) + 1
        avg_df.drop(["date", "amount"], axis = 1, inplace = True)
        o = pd.merge(left=pd.DataFrame(self.plan.product_no.unique(), columns=["product_no"]), right=avg_df, how="left", left_on="product_no", right_on="product_no").fillna(avg_df.order_amount.mean().__floordiv__(1))
        o.set_index(keys="product_no", inplace=True)
        # avg_df.drop(["date", "amount"], inplace = True, axis = 1)
        # AVERAGE ORDER SIZE

        # SETUP TIMES
        st = pd.merge(left=production_path.transpose(), right=self.setup, how="left", left_on=1, right_on="stations_list").iloc[:, [0, 2]].copy()
        st[st.columns[1]] = st[st.columns[1]].fillna(0)
        st.set_index(keys=[1], inplace=True)
        st = st.transpose()
        # SETUP TIMES

        # OUTSOURCE AVAILABILITY
        outsource_perm = pd.merge(left=production_path.transpose(), right=self.machine_info, how="left", left_on = 1, right_on="machine").loc[:, [production_path.transpose().columns[0], "outsource_availability"]].copy()
        outsource_perm[outsource_perm.columns[1]] = outsource_perm[outsource_perm.columns[1]].fillna(0)
        outsource_perm.set_index(keys=[1], inplace=True)
        outsource_perm = outsource_perm.transpose()
        # OUTSOURCE AVAILABILITY

        # Creation of h(times), k(binary), d(order), f(amount), s(shift) and c(cost) tables
        df = df.groupby(["product_no", "station"], as_index = False).agg({"cycle_times": sum})
        h = df.pivot("product_no", "station", "cycle_times").fillna(0)
        k = df.copy()
        k.at[k.cycle_times > 0, "cycle_times"] = 1
        k = k.pivot("product_no", "station", "cycle_times").fillna(0)
        h = h[machine_legend.iloc[:, 0].to_list()]
        k = k[machine_legend.iloc[:, 0].to_list()]
        f = machine_info_df["quantity"].to_frame().transpose().copy()
        s = machine_info_df["shift"].to_frame().transpose().copy()
        c = DataFrame(index = [1, 2, 3], columns = [1], data = [0, 23, 151]).transpose()
        if pivot:
            d = self.pivot_days()
        else:
            d = self.plan.copy()
        for curr_table in [d, h, k, o]:
            curr_table.index = list(range(1, curr_table.shape[0] + 1))
        for curr_table in [h, k, st, outsource_perm]:
            curr_table.columns = list(range(1, curr_table.shape[1] + 1))
        return product_no_legend, machine_legend, d, h, k, f, s, c, o, st, outsource_perm

    def get_attrs(self):
        return self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.machine_cnt, self.shift, self.cost

    def create_file(self, file_dir):
        self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.machine_cnt, self.shift, self.cost, self.order_averages, self.setup_time, self.outsource_perm = self.create_tables()
        create_xl_file(self, file_dir, "operational_math_model")


class TacticalMMInput:
    def __init__(self, parent, forecast):
        self.merged_file = parent.merged_file.copy()
        self.machine_info = parent.machine_info.copy()
        self.order_history = parent.order_history
        self.setup = parent.temp.copy()
        self.product_family_legend = None
        self.machine_legend = None
        self.forecast = forecast
        self.times = None
        self.route_prob = None
        self.machine_cnt = None
        self.workdays = None
        self.budget = None
        self.cost = None
        self.machine_price = None
        self.average_order = None
        self.setup_times = None
        self.outsource_availability = None
        self.order_time_parameters = None
        self.probabilities = None
        # Placeholder
        self.forecast = parent.order_history.agg(pivot = True).iloc[:, -12:]

    @staticmethod
    def create_scenarios(forecast):
        temp_forecast = forecast.copy()
        temp_forecast.drop(temp_forecast[temp_forecast.sum(axis = 1) == 0].index, inplace = True)
        forecast_index = temp_forecast.index
        temp_forecast = temp_forecast.reindex(temp_forecast.index.repeat(5))
        temp_forecast.reset_index(inplace = True)
        temp_forecast.iloc[::5, -12:] = temp_forecast.iloc[::5, -12:].sub(temp_forecast.iloc[::5, -12:].std(axis = 1)*1,
                                                                          axis = 0)
        temp_forecast.iloc[1::5, -12:] = temp_forecast.iloc[1::5, -12:].sub(
            temp_forecast.iloc[1::5, -12:].std(axis = 1)*0.5,
            axis = 0)
        temp_forecast.iloc[3::5, -12:] = temp_forecast.iloc[3::5, -12:].add(
            temp_forecast.iloc[3::5, -12:].std(axis = 1)*0.5,
            axis = 0)
        temp_forecast.iloc[4::5, -12:] = temp_forecast.iloc[4::5, -12:].add(
            temp_forecast.iloc[4::5, -12:].std(axis = 1)*1,
            axis = 0)
        num_forecast = temp_forecast._get_numeric_data()
        num_forecast[num_forecast < 0] = 0
        num_forecast.astype(int)
        temp_forecast.iloc[:, -12:] = num_forecast
        temp_forecast["new_index"] = [1, 2, 3, 4, 5]*forecast_index.nunique()
        temp_forecast.set_index(keys = [temp_forecast.columns[0], "new_index"], inplace = True)
        temp_forecast.index.names = ["", ""]
        return temp_forecast

    def cross_trim(self):
        # Placeholder
        self.forecast = extract_forecast(self.forecast)
        forecast_idx = self.forecast.index.to_list()
        bom_idx = self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).isin(forecast_idx)
        self.merged_file.drop(self.merged_file[~bom_idx].index, inplace = True)
        self.forecast.drop(self.forecast[~self.forecast.index.to_series().isin(
            list(self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).unique()))].index, inplace = True)
        self.merged_file.reset_index(inplace = True, drop = True)

    def set_order_times(self, l: list):
        self.order_time_parameters = pd.DataFrame(data=l, index=[1, 2]).transpose()

    def set_probabilities(self, l: list):
        self.probabilities = pd.DataFrame(data=l, index=[1, 2, 3, 4, 5]).transpose()

    def create_tables(self):
        self.cross_trim()
        product_family_legend = DataFrame(
            list(self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).unique()),
            columns = ["product_family"])
        prod_path = self.merged_file.groupby(by = "station", as_index = False).agg({"level": "mean"})
        prod_path.sort_values(by = "level", ascending = False, inplace = True)
        machine_legend = DataFrame(prod_path.station.to_list(), columns = ["station"])

        bom_data = self.merged_file.copy()
        bom_data.amount = bom_data.amount.astype(int)
        bom_data.cycle_times = bom_data.cycle_times.astype(float)
        bom_data.cycle_times = bom_data.amount*bom_data.cycle_times.astype(float)
        bom_data.drop(joining_indices(bom_data), inplace = True)
        bom_data.drop(
            bom_data[bom_data.product_no.eq(bom_data.product_no.shift(1, fill_value = 0)) & bom_data.level.eq(1)].index,
            inplace = True)
        bom_data = bom_data.groupby(by = ["product_no", "station"], as_index = False).agg({"cycle_times": "sum"})
        bom_data["product_family"] = bom_data.product_no.str.split(".").apply(lambda x: x[0])
        prod_cnt = {x: bom_data[bom_data.product_family == x].product_no.nunique() for x in
                    list(bom_data.product_family.unique())}
        bom_data = bom_data.groupby(by = ["product_family", "station"], as_index = False).agg(
            {"cycle_times": "mean", "product_no": "count"})
        bom_data.columns = ["product_family", "station", "cycle_times", "product_count"]
        bom_data["probability"] = bom_data.product_count/bom_data.product_family.replace(prod_cnt)

        machine_info_df = merge(left = machine_legend, right = self.machine_info, how = "left", left_on = "station",
                                right_on = "machine").fillna(1).iloc[:, [0, 2, 3, 4, 5]]

        # AVERAGE ORDER SIZE
        avg_df = self.order_history.orders.copy()
        avg_df["product_family"] = avg_df.product_no.str.split(".").apply(lambda x: x[0])
        avg_df = avg_df.groupby("product_family", as_index = False).agg({"date": "count", "amount": "sum"})
        avg_df["order_amount"] = avg_df.amount/avg_df.date
        avg_df.order_amount = avg_df.order_amount.floordiv(1) + 1
        avg_df.drop(["date", "amount"], axis = 1, inplace = True)
        o = pd.merge(left=pd.DataFrame(product_family_legend.product_family.unique(), columns=["product_family"]), right=avg_df, how="left", left_on="product_family", right_on="product_family").fillna(avg_df.order_amount.mean().__floordiv__(1))
        o.set_index(keys="product_family", inplace=True)
        # avg_df.drop(["date", "amount"], inplace = True, axis = 1)
        # AVERAGE ORDER SIZE

        # SETUP TIMES
        st = pd.merge(left=prod_path.station, right=self.setup, how="left", left_on="station", right_on="stations_list").iloc[:, [0, 2]].copy()
        st[st.columns[1]] = st[st.columns[1]].fillna(0)
        st.set_index(keys="station", inplace=True)
        st = st.transpose()
        # SETUP TIMES

        # OUTSOURCE AVAILABILITY
        outsource_perm = pd.merge(left=prod_path.station, right=self.machine_info, how="left", left_on = "station", right_on="machine").loc[:, ["station", "outsource_availability"]].copy()
        outsource_perm[outsource_perm.columns[1]] = outsource_perm[outsource_perm.columns[1]].fillna(0)
        outsource_perm.set_index(keys="station", inplace=True)
        outsource_perm = outsource_perm.transpose()
        # OUTSOURCE AVAILABILITY


        d = self.forecast.copy()
        h = bom_data.pivot("product_family", "station", "cycle_times").fillna(0)
        h = h[machine_info_df[machine_info_df.columns[0]]].copy()
        k = bom_data.pivot("product_family", "station", "probability").fillna(0)
        k = k[machine_info_df[machine_info_df.columns[0]]].copy()
        f = machine_info_df["quantity"].to_frame().transpose().copy()
        # Workdays will be implemented
        w = DataFrame([25, 24, 25, 25, 25, 19, 26, 23, 25, 25, 26, 23], index = list(range(1, 13))).transpose()
        # Budget part will be implemented
        # b = DataFrame([100000]*12, index = list(range(1, 13))).transpose()
        # Costs will be implemented
        c = DataFrame([20, 23, 151], index = [1, 2, 3]).transpose()
        # Machine costs will be implemented
        cr = merge(left=prod_path, right=machine_info_df, how="left", left_on = "station", right_on = "station").fillna(0)["procurement_cost"].to_frame().transpose()

        for curr_df in [product_family_legend, machine_legend, d, h, k, f, o, st, cr, outsource_perm]:
            curr_df.index = list(range(1, curr_df.shape[0] + 1))
            curr_df.columns = list(range(1, curr_df.shape[1] + 1))

        d = self.create_scenarios(d)
        d = d.astype(int)

        return product_family_legend, machine_legend, d, h, k, f, w, c, cr, o, st, outsource_perm

    def create_file(self, file_dir):
        self.product_family_legend, self.machine_legend, self.forecast, self.times, self.route_prob, self.machine_cnt, self.workdays, self.cost, self.machine_price, self.average_order, self.setup_times, self.outsource_availability = self.create_tables()
        create_xl_file(self, file_dir, "tactical_math_model")


if __name__ == "__main__":
    # If a callback is not being made;
    # model = ArchiveDatabase()
    # model.load_files_to_be_deleted(constants.tbd_path)
    # model.load_bom(constants.bom_path)
    # model.load_times(constants.times_path)
    # model.load_order_history()
    # model.merge_files()
    # If a callback is made;
    model = revert_checkpoint("../19_nisan.mng")
    # op_input_file = OperationalSMInput(model)
    # op_input_file.load_plan("C://sl_data//xlsx//aralik_plan.xlsx")
    # op_input_file.create_tables()
    # op_input_file.create_file("C:\\sl_data\\mango.xlsx")
    # tac_input_file = TacticalSMInput(model)
    # tac_input_file.create_tables()
    # tac_input_file.create_file("C:\\sl_data\\mango_tactical.xlsx")

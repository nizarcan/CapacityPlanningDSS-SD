from app_backend.utils.df_ops import arrange_df, merge_bom_and_times, trim_df, create_operational_table, \
    create_tactical_table, trim_order, format_machine_names
from app_backend.utils.xl_ops import load_file, load_plan, add_plan, create_xl_file
from pandas import DataFrame, concat, merge, to_timedelta
from app_backend.utils.demand_util import OrderHistory, extract_forecast
from app_backend.utils.finder import joining_indices
import pickle


def revert_checkpoint(file_dir):
    with open(file_dir, "rb") as f:
        mdl = pickle.load(f)
        return mdl


class FileSkeleton:
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
        self.last_callback_date = None

    def __repr__(self):
        if self.last_callback_date is None:
            return "An input file struct that holds the data but hasn't yet compiled and created a backup."
        else:
            return f"An input file struct that holds the data that is compiled at {self.last_callback_date}."

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
        # Plan init
        self.plan = None

    def load_plan(self, file_dir):
        if not bool(self.plan_count):
            self.plan = load_plan(file_dir)
        else:
            self.plan = add_plan(self.plan, file_dir)
        self.plan_count += 1

    def trim_bom(self):
        self.merged_file, missing_dict = trim_df(self.merged_file, self.plan)
        self.plan.product_no.replace(missing_dict, inplace = True)

    def create_tables(self):
        self.trim_bom()
        self.legend_table = create_operational_table(self.merged_file, "legend")
        self.input_table = create_operational_table(self.merged_file, "input")
        self.duplication_matrix = create_operational_table(self.merged_file, "dup")
        self.sequence_matrix = create_operational_table(self.merged_file, "sequence")
        self.time_matrix = create_operational_table(self.merged_file, "time")
        self.join_matrix, self.join_amount_table = create_operational_table(self.merged_file, "joins")
        self.set_list_table = create_operational_table(self.temp, "set_list")
        self.order_table = create_operational_table(self.plan, "order", self.merged_file, self.plan_count)

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
        self.cross_trim()
        self.product_no_legend = None
        self.machine_legend = None
        self.times = None
        self.route_prob = None
        self.machine_cnt = None
        self.shift = None
        self.cost = None

    def cross_trim(self):
        self.plan = self.plan[self.plan.product_no.isin(self.merged_file.product_no)].copy()
        self.merged_file.drop(self.merged_file[~self.merged_file.product_no.isin(self.plan.product_no)].index,
                              inplace = True)
        self.merged_file.reset_index(inplace = True, drop = True)
        self.plan.reset_index(inplace = True, drop = True)

    def pivot_days(self):
        df = self.plan.copy()
        df = df.groupby(by = ["product_no", "start_date"], as_index = False).agg({"amount": "sum"})
        df["new_day"] = to_timedelta(df.start_date - df.start_date.min())
        df["new_day"] = df["new_day"].apply(lambda x: x.days + 1)
        return df.pivot("product_no", "new_day", "amount").fillna(0)

    def update_machine_info(self, file_dir):
        df = load_file(file_dir)
        df[df.columns[0]] = format_machine_names(df, df.columns[0])
        df = concat([self.machine_info[~self.machine_info["machine"].isin(df[df.columns[0]].to_list())], df])
        df.reset_index(inplace = True, drop = True)
        self.machine_info = df.copy()

    def create_tables(self, pivot=True):
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
        product_no_legend = DataFrame(df.product_no.unique().tolist(), columns = ["product_no"])
        machine_info_df = merge(left = machine_legend, right = self.machine_info, how = "left", left_on = "station",
                                right_on = "machine").fillna(1).iloc[:, [0, 2, 3]]
        machine_info_df.index = list(range(1, machine_info_df.shape[0] + 1))

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
        for curr_table in [d, h, k]:
            curr_table.index = list(range(1, curr_table.shape[0] + 1))
        for curr_table in [h, k]:
            curr_table.columns = list(range(1, curr_table.shape[1] + 1))
        return product_no_legend, machine_legend, d, h, k, f, s, c

    def get_attrs(self):
        return self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.machine_cnt, self.shift, self.cost

    def create_file(self, file_dir):
        self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.machine_cnt, self.shift, self.cost = self.create_tables()
        create_xl_file(self, file_dir, "operational_math_model")


class TacticalMMInput:
    def __init__(self, parent, forecast):
        self.merged_file = parent.merged_file.copy()
        self.machine_info = parent.machine_info.copy()
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
        # Placeholder
        self.forecast = parent.order_history.agg(pivot = True)

    def cross_trim(self):
        # Placeholder
        forecast_idx = extract_forecast(self.forecast).index.to_list()
        bom_idx = self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).isin(forecast_idx)
        self.merged_file.drop(self.merged_file[~bom_idx].index, inplace = True)
        self.forecast.drop(self.forecast[~self.forecast.index.to_series().isin(forecast_idx)].index, inplace = True)
        self.merged_file.reset_index(inplace = True, drop = True)

    def create_tables(self):
        self.cross_trim()
        product_family_legend = DataFrame(self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).to_list(),
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
        prod_cnt = {x: bom_data[bom_data.product_family == x].product_family.nunique() for x in
                    list(bom_data.product_family.unique())}
        bom_data = bom_data.groupby(by = ["product_family", "station"], as_index = False).agg(
            {"cycle_times": "mean", "product_no": "count"})
        bom_data.columns = ["product_family", "station", "cycle_times", "product_count"]
        bom_data["probability"] = bom_data.product_family.replace(prod_cnt)/bom_data.product_count

        machine_info_df = merge(left = machine_legend, right = self.machine_info, how = "left", left_on = "station",
                                right_on = "machine").fillna(1).iloc[:, [0, 2, 3]]

        d = self.forecast.copy()
        h = bom_data.pivot("product_family", "station", "cycle_times").fillna(0)
        k = bom_data.pivot("product_family", "station", "probability").fillna(0)
        f = machine_info_df["quantity"].to_frame().transpose().copy()
        # Workdays will be implemented
        w = DataFrame([25, 24, 25, 25, 25, 19, 26, 23, 25, 25, 26, 23], index = list(range(1, 13))).transpose()
        # Budget part will be implemented
        b = DataFrame([100000]*12, index = list(range(1, 13))).transpose()
        # Costs will be implemented
        c = DataFrame([20, 23, 30], index = [1, 2, 3]).transpose()
        # Machine costs will be implemented
        cr = DataFrame([100000]*f.shape[1], index = list(range(1, f.shape[1] + 1))).transpose()

        return product_family_legend, machine_legend, d, h, k, f, w, b, c, cr

    def create_file(self, file_dir):
        self.product_family_legend, self.machine_legend, self.forecast, self.times, self.route_prob, self.machine_cnt, self.workdays, self.budget, self.cost, self.machine_price = self.create_tables()
        create_xl_file(self, file_dir, "tactical_math_model")


if __name__ == "__main__":
    # If a callback is not being made;
    # model = FileSkeleton()
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

from backend.utils.xl_ops import load_file, load_plan, add_plan, create_xl_file
from backend.compiler import revert_checkpoint, ArchiveDatabase
from backend.utils.finder import product_numerator, joining_indices
from backend.utils.demand_util import extract_forecast
import backend.constants as constants
import numpy as np
import pandas as pd


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
        self.forecast = parent.order_history.agg(pivot = True).iloc[:, -12:]

    def cross_trim(self):
        # Placeholder
        self.forecast = extract_forecast(self.forecast)
        forecast_idx = self.forecast.index.to_list()
        bom_idx = self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).isin(forecast_idx)
        self.merged_file.drop(self.merged_file[~bom_idx].index, inplace = True)
        self.forecast.drop(self.forecast[~self.forecast.index.to_series().isin(list(self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).unique()))].index, inplace = True)
        self.merged_file.reset_index(inplace = True, drop = True)

    def create_tables(self):
        self.cross_trim()
        product_family_legend = pd.DataFrame(list(self.merged_file.product_no.str.split(".").apply(lambda x: x[0]).unique()),
                                          columns = ["product_family"])
        prod_path = self.merged_file.groupby(by = "station", as_index = False).agg({"level": "mean"})
        prod_path.sort_values(by = "level", ascending = False, inplace = True)
        machine_legend = pd.DataFrame(prod_path.station.to_list(), columns = ["station"])

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
        bom_data["probability"] = bom_data.product_count / bom_data.product_family.replace(prod_cnt)

        machine_info_df = pd.merge(left = machine_legend, right = self.machine_info, how = "left", left_on = "station",
                                right_on = "machine").fillna(1).iloc[:, [0, 2, 3]]

        d = self.forecast.copy()
        h = bom_data.pivot("product_family", "station", "cycle_times").fillna(0)
        h = h[machine_info_df[machine_info_df.columns[0]]].copy()
        k = bom_data.pivot("product_family", "station", "probability").fillna(0)
        k = k[machine_info_df[machine_info_df.columns[0]]].copy()
        f = machine_info_df["quantity"].to_frame().transpose().copy()
        # Workdays will be implemented
        w = pd.DataFrame([25, 24, 25, 25, 25, 19, 26, 23, 25, 25, 26, 23], index = list(range(1, 13))).transpose()
        # Budget part will be implemented
        # b = pd.DataFrame([100000]*12, index = list(range(1, 13))).transpose()
        # Costs will be implemented
        c = pd.DataFrame([20, 23, 30], index = [1, 2, 3]).transpose()
        # Machine costs will be implemented
        cr = pd.DataFrame([100000]*f.shape[1], index = list(range(1, f.shape[1] + 1))).transpose()

        for curr_df in [product_family_legend, machine_legend, d, h, k, f]:
            curr_df.index = list(range(1, curr_df.shape[0]+1))
            curr_df.columns = list(range(1, curr_df.shape[1]+1))

        self.product_family_legend, self.machine_legend, self.forecast, self.times, self.route_prob, self.machine_cnt, self.workdays, self.cost, self.machine_price = product_family_legend, machine_legend, d, h, k, f, w, c, cr
        # return product_family_legend, machine_legend, d, h, k, f, w, c, cr

    def create_file(self, file_dir):
        # self.product_family_legend, self.machine_legend, self.forecast, self.times, self.route_prob, self.machine_cnt, self.workdays, self.cost, self.machine_price = self.create_tables()
        create_xl_file(self, file_dir, "tactical_math_model")



class OperationalMathModel:
    def __init__(self, parent):
        self.merged_file = parent.merged_file
        orders = parent.order_history.pivot()
        self.order = orders[orders.index.isin(self.merged_file.product_no)][orders.columns[-12:]].copy()
        self.order.drop(self.order[self.order == 0].index, inplace=True)
        self.merged_file.drop(self.merged_file[~self.merged_file.product_no.isin(self.order.index)].index, inplace=True)
        self.merged_file.reset_index(inplace=True, drop=True)


def create_table(df):
    df1 = df.copy()
    df1.amount = df1.amount.astype(int)
    df1.cycle_times = df1.cycle_times.astype(float)
    df1.cycle_times = df1.amount*df1.cycle_times.astype(float)
    df1.drop(joining_indices(df1), inplace = True)
    df1.drop(df1[df1.product_no.eq(df1.product_no.shift(1, fill_value = 0)) & df1.level.eq(1)].index, inplace = True)
    production_path = df1.groupby("station", as_index = False).agg({"level": np.mean})
    production_path.sort_values("level", ascending = False, inplace = True)
    machine_legend_table = production_path["station"].copy()
    machine_legend_table.index = list(range(1, machine_legend_table.shape[0] + 1))
    machine_legend_table = machine_legend_table.to_frame()
    production_path.drop("level", axis = 1, inplace = True)
    production_path.columns = [1]
    production_path = production_path.transpose()
    production_path.columns = list(range(1, production_path.shape[1] + 1))
    df1 = df1.groupby(["product_no", "station"], as_index = False).agg({"cycle_times": sum})
    product_family_legend_table = pd.DataFrame(df1.product_no.unique().tolist(), columns = ["product_no"],
                                               index = list(range(1, len(df1.product_no.unique().tolist()) + 1)))
    prod_count = df1.product_no.nunique()
    grouped_df = df1.groupby("station", as_index=False).agg({"product_no": "count", "cycle_times": ["min", "mean", "max"]})
    grouped_df.columns = ["station", "product_no", "min", "mean", "max"]
    temp_df = pd.merge(left = production_path.transpose(), right = grouped_df, how = "left", left_on = 1, right_on = "station")
    # station_path = temp_df.station.transpose()
    # probabilities = (temp_df.product_no/prod_count).transpose()
    # times = temp_df.cycle_times.transpose()
    return temp_df


if __name__ == "__main__":
    model = revert_checkpoint(constants.archive_file_path)
    new = TacticalMMInput(model, "f")
    # stat, prob, time = create_table(new.merged_file)
    # out_df = create_table(new.merged_file)
    new.create_tables()

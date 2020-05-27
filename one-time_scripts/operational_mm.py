from backend.utils.xl_ops import load_plan, load_file, create_xl_file
from backend.compiler import revert_checkpoint, ArchiveDatabase
from backend.utils.finder import product_numerator, joining_indices
from backend.utils.df_ops import format_machine_names
import backend.constants as constants
from pandas import to_timedelta, DataFrame, concat, merge
import numpy as np


class OperationalMathModel:
    def __init__(self, parent, file_dir):
        self.merged_file = parent.merged_file
        self.plan = load_plan(file_dir)
        self.machine_info = parent.machine_info
        self.cross_trim()
        self.product_no_legend = []
        self.machine_legend = []
        self.times = []
        self.route_prob = []
        self.amount = []
        self.shift = []
        self.cost = []

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
        production_path = df.groupby("station", as_index = False).agg({"level": np.mean})
        production_path.sort_values("level", ascending = False, inplace = True)
        machine_legend = production_path["station"].copy()
        machine_legend.index = list(range(1, machine_legend.shape[0] + 1))
        machine_legend = machine_legend.to_frame()
        production_path.drop("level", axis = 1, inplace = True)
        production_path.columns = [1]
        production_path = production_path.transpose()
        production_path.columns = list(range(1, production_path.shape[1] + 1))
        product_no_legend = DataFrame(df.product_no.unique().tolist(), columns = [1])
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
        c = DataFrame(index = list(range(1, 4)), columns = [1], data = [0, 23, 151])
        if pivot:
            d = self.pivot_days()
        else:
            d = self.plan.copy()
        for curr_table in [d, h, k]:
            curr_table.index = list(range(1, curr_table.shape[0]+1))
        return product_no_legend, machine_legend, d, h, k, f, s, c

    def get_attrs(self):
        return self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.amount, self.shift, self.cost

    def create_file(self, file_dir):
        self.product_no_legend, self.machine_legend, self.plan, self.times, self.route_prob, self.amount, self.shift, self.cost = self.create_tables()
        create_xl_file(self, file_dir, "operational_math_model")


if __name__ == "__main__":
    model = revert_checkpoint("../18_nisan.mng")
    new = OperationalMathModel(model, constants.aralik_order_path)
    _, mchn_legend, _, _, _, _, _, _ = new.create_tables()
    # df1, mlt, h1, k1 = create_table(new.merged_file, "a")

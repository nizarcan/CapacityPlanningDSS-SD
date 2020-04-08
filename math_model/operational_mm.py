from app_backend.backend_parser import revert_checkpoint, InputFileSkeleton
from app_backend.utils.finder import product_numerator, joining_indices
import numpy as np


class OperationalMathModel:
    def __init__(self, parent):
        self.merged_file = parent.merged_file
        self.order = parent.order_history[parent.order_history.index.isin(self.merged_file.product_no)][parent.order_history.columns[-1]].copy()
        self.order.drop(self.order[self.order == 0].index, inplace=True)
        self.merged_file.drop(self.merged_file[~self.merged_file.product_no.isin(self.order.index)].index, inplace=True)
        self.merged_file.reset_index(inplace=True, drop=True)


def create_table(df, df_type):
    df = df.copy()
    df.amount = df.amount.astype(int)
    df.cycle_times = df.cycle_times.astype(float)
    df.cycle_times = df.amount*df.cycle_times.astype(float)
    df.drop(joining_indices(df), inplace = True)
    df.drop(df[df.product_no.eq(df.product_no.shift(1, fill_value = 0)) & df.level.eq(1)].index, inplace = True)
    production_path = df.groupby("station", as_index = False).agg({"level": np.mean})
    production_path.sort_values("level", ascending = False, inplace = True)
    machine_legend_table = production_path["station"].copy()
    machine_legend_table.index = list(range(1, machine_legend_table.shape[0] + 1))
    machine_legend_table = machine_legend_table.to_frame()
    production_path.drop("level", axis = 1, inplace = True)
    production_path.columns = [1]
    production_path = production_path.transpose()
    production_path.columns = list(range(1, production_path.shape[1] + 1))
    df = df.groupby(["product_no", "station"], as_index = False).agg({"cycle_times": sum})
    h = df.pivot("product_no", "station", "cycle_times").fillna(0)
    k = df.copy()
    k.at[k.cycle_times > 0, "cycle_times"] = 1
    k = k.pivot("product_no", "station", "cycle_times").fillna(0)
    return df, machine_legend_table, h, k


if __name__ == "__main__":
    model = revert_checkpoint("../10_mart.mng")
    new = OperationalMathModel(model)
    df1, mlt, h1, k1 = create_table(new.merged_file, "a")
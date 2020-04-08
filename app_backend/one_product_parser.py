from app_backend.backend_parser import revert_checkpoint, InputFileSkeleton
from app_backend.utils.finder import product_numerator, joining_indices
import numpy as np
import pandas as pd


class OperationalMathModel:
    def __init__(self, parent):
        self.merged_file = parent.merged_file
        self.order = parent.order_history[parent.order_history.index.isin(self.merged_file.product_no)][parent.order_history.columns[-1]].copy()
        self.order.drop(self.order[self.order == 0].index, inplace=True)
        self.merged_file.drop(self.merged_file[~self.merged_file.product_no.isin(self.order.index)].index, inplace=True)
        self.merged_file.reset_index(inplace=True, drop=True)


def create_table(df):
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
    product_family_legend_table = pd.DataFrame(df.product_no.unique().tolist(), columns = ["product_no"],
                                               index = list(range(1, len(df.product_no.unique().tolist()) + 1)))
    prod_count = df.product_no.nunique()
    grouped_df = df.groupby("station", as_index=False).agg({"product_no": "count", "cycle_times": ["min", "mean", "max"]})
    grouped_df.columns = ["station", "product_no", "min", "mean", "max"]
    temp_df = pd.merge(left = production_path.transpose(), right = grouped_df, how = "left", left_on = 1, right_on = "station")
    # station_path = temp_df.station.transpose()
    # probabilities = (temp_df.product_no/prod_count).transpose()
    # times = temp_df.cycle_times.transpose()
    return temp_df


if __name__ == "__main__":
    model = revert_checkpoint("../10_mart.mng")
    new = OperationalMathModel(model)
    # stat, prob, time = create_table(new.merged_file)
    df = create_table(new.merged_file)

import pickle
from app_backend.utils.xl_ops import load_file, load_plan, add_plan, create_op_input_file, create_tac_input_file
from app_backend.utils.df_ops import arrange_df, merge_bom_and_times, trim_df, create_operational_table, create_tactical_table, trim_order
from app_backend.utils.demand_util import demand_parser


def revert_checkpoint(file_dir):
    with open(file_dir, "rb") as f:
        mdl = pickle.load(f)
        return mdl


class InputFileSkeleton:
    def __init__(self):
        self.bom_file = []
        self.times_file = []
        self.files_to_be_deleted = []
        self.order_history = []
        self.merged_file = []
        self.assembly_df = []
        self.cmy_df = []
        self.temp = []
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

    def load_order_history(self):
        self.order_history = demand_parser(agg=True)

    def merge_files(self):
        self.merged_file = merge_bom_and_times(self.bom_file, self.times_file)
        self.merged_file = arrange_df(self.merged_file, "merged", assembly_df = self.assembly_df)


class OperationalInput:
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
        self.plan = []

    def load_plan(self, file_dir):
        if not bool(self.plan_count):
            self.plan = load_plan(file_dir)
        else:
            self.plan = add_plan(self.plan, file_dir)
        self.plan_count += 1

    def trim_bom(self):
        self.merged_file, missing_dict = trim_df(self.merged_file, self.plan)
        self.plan.product_no.replace(missing_dict, inplace=True)

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
        create_op_input_file(self, file_dir)


class TacticalInput:
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
        self.prod_family_legend_table, self.machine_legend_table, self.sequence_list, self.min_matrix, self.mean_matrix, self.max_matrix, self.prob_matrix = create_tactical_table(self.merged_file, table_type = "mult")
        self.set_list_table = create_tactical_table(self.temp, "set_list")
        self.order_table = create_tactical_table(self.order_history, "order")

    def create_file(self, file_dir):
        create_tac_input_file(self, file_dir)


if __name__ == "__main__":
    # If a callback is not being made;
    # model = InputFileSkeleton()
    # model.load_files_to_be_deleted(constants.tbd_path)
    # model.load_bom(constants.bom_path)
    # model.load_times(constants.times_path)
    # model.load_order_history()
    # model.merge_files()
    # If a callback is made;
    model = revert_checkpoint("../10_mart.mng")
    op_input_file = OperationalInput(model)
    op_input_file.load_plan("C://sl_data//xlsx//aralik_plan.xlsx")
    op_input_file.create_tables()
    # op_input_file.create_file("C:\\sl_data\\mango.xlsx")
    # tac_input_file = TacticalInput(model)
    # tac_input_file.create_tables()
    # tac_input_file.create_file("C:\\sl_data\\mango_tactical.xlsx")

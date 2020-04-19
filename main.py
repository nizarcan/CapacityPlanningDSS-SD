from app_backend.backend_composer import FileSkeleton, OperationalSMInput, OperationalMMInput, TacticalSMInput, revert_checkpoint
from app_backend.utils.demand_util import OrderHistory
import app_backend.constants as constants

if __name__ == "__main__":
    # model = FileSkeleton()
    # model.load_files_to_be_deleted(constants.tbd_path)
    # model.load_machine_info(constants.machine_info_path)
    # model.load_bom(constants.bom_path)
    # model.load_times(constants.times_path)
    # model.merge_files()
    model = revert_checkpoint("18_nisan.mng")
    # op_input_file = OperationalSMInput(model)
    # op_input_file.load_plan(constants.aralik_order_path)
    # op_input_file.load_plan(constants.ocak_order_path)
    # op_input_file.create_tables()
    # op_input_file.create_file("C:\\sl_data\\mango_operational.xlsx")
    # tac_input_file = TacticalSMInput(model)
    # tac_input_file.create_tables()
    # tac_input_file.create_file("C:\\sl_data\\mango_tactical.xlsx")
    # op_mm = OperationalMMInput(model, constants.aralik_order_path)
    # op_mm.create_file("C://sl_data//xlsx//op_mm_aralik.xlsx")
    past_demand = OrderHistory

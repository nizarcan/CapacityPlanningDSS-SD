from app_backend.backend_parser import InputFileSkeleton, OperationalInput, TacticalInput, revert_checkpoint
import app_backend.constants as constants

if __name__ == "__main__":
    model = revert_checkpoint("10_mart.mng")
    op_input_file = OperationalInput(model)
    op_input_file.load_plan(constants.aralik_order_path)
    op_input_file.load_plan(constants.ocak_order_path)
    op_input_file.create_tables()
    # op_input_file.create_file("C:\\sl_data\\mango_operational.xlsx")
    tac_input_file = TacticalInput(model)
    tac_input_file.create_tables()
    # tac_input_file.create_file("C:\\sl_data\\mango_tactical.xlsx")

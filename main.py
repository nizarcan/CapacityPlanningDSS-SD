from app_backend.compiler import ArchiveDatabase, OperationalSMInput, OperationalMMInput, TacticalSMInput, TacticalMMInput, revert_checkpoint
# from app_backend.utils.demand_util import OrderHistory
import app_backend.constants as constants


def create_archive():
    model = ArchiveDatabase()
    model.load_files_to_be_deleted(constants.tbd_path)
    model.load_machine_info(constants.machine_info_path)
    model.load_bom(constants.bom_path)
    model.load_times(constants.times_path)
    model.initialize_order_history()
    model.merge_files()
    model.save_checkpoint(constants.archive_file_path)
    return model


def load_archive():
    return revert_checkpoint(constants.archive_file_path)


def create_operational_simulation(model, output_dir):
    op_input_file = OperationalSMInput(model)
    op_input_file.load_plan("C://sl_data//xlsx//aralik_new_plan.xlsx")
    op_input_file.load_plan("C://sl_data//xlsx//aralik_new_plan.xlsx")
    op_input_file.load_days("C://sl_data//xlsx//aralik_gunler.xlsx")
    op_input_file.load_math_model_output("C://sl_data//xlsx//okpm_results.xlsx")
    op_input_file.create_tables()
    op_input_file.create_file(output_dir)
    return op_input_file


def create_operational_math_model(model):
    out_struct = OperationalMMInput(model, "C://sl_data//xlsx//eylul_plan.xlsx")
    out_struct.load_days("C://sl_data//xlsx//eylul_gunler.xlsx")
    out_struct.create_file(constants.okpm_parameters)
    return out_struct


def create_tactical_simulation(model):
    tac_input_file = TacticalSMInput(model)
    tac_input_file.create_tables()
    tac_input_file.create_file("C:\\sl_data\\tactical_simulation.xlsx")


def create_tactical_math_model(model):
    tacmm = TacticalMMInput(model, "forecast")
    tacmm.create_file("tactical_math_model.xlsx")
    return tacmm


if __name__ == "__main__":
    # archive = create_archive()
    archive = load_archive()
    op_sm = create_operational_simulation(archive, "D:\\Nizar\\Desktop\\Aralik_Aralik_OKPB_Input.xlsx")
    # create_tactical_simulation(archive)
    # op_mm = create_operational_math_model(archive)
    # tmm = create_tactical_math_model(archive)

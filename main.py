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


def create_operational_simulation(model):
    op_input_file = OperationalSMInput(model)
    op_input_file.load_plan(constants.plans["aralik"])
    op_input_file.load_plan(constants.plans["aralik"])
    op_input_file.load_days(constants.days["aralik"])
    op_input_file.load_math_model_output(constants.results["OperationalMMInput"])
    op_input_file.create_tables()
    op_input_file.create_file(constants.outputs["OperationalSMInput"])
    return op_input_file


def create_operational_math_model(model):
    out_struct = OperationalMMInput(model, constants.plans["eylul"])
    out_struct.load_days(constants.days["eylul"])
    out_struct.create_file(constants.results["OperationalMMInput"])
    return out_struct


def create_tactical_simulation(model):
    tac_input_file = TacticalSMInput(model)
    tac_input_file.create_tables()
    tac_input_file.create_file("C:\\sl_data\\tactical_simulation.xlsx")


def create_tactical_math_model(model):
    tacmm = TacticalMMInput(model, "forecast")
    tacmm.create_file(constants.outputs["TacticalMMInput"])
    return tacmm


if __name__ == "__main__":
    # archive = create_archive()
    archive = load_archive()
    op_sm = create_operational_simulation(archive)
    # create_tactical_simulation(archive)
    # op_mm = create_operational_math_model(archive)
    # tmm = create_tactical_math_model(archive)

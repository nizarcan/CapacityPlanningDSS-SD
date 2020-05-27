from backend.compiler import ArchiveDatabase, OperationalSMInput, OperationalMMInput, TacticalSMInput, TacticalMMInput, revert_checkpoint
# from app_backend.utils.demand_util import OrderHistory
import backend.constants as constants


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


def create_operational_simulation(model, ay):
    op_input_file = OperationalSMInput(model)
    op_input_file.load_plan(constants.plans[ay])
    op_input_file.load_plan(constants.plans[ay])
    op_input_file.load_days(constants.days[ay])
    op_input_file.load_math_model_output(constants.results["OperationalMMInput"])
    op_input_file.create_tables()
    op_input_file.create_file(constants.output_path)
    return op_input_file


def create_operational_math_model(model, ay, senaryo):
    out_struct = OperationalMMInput(model, constants.plans[ay], senaryo)
    out_struct.load_days(constants.days[ay])
    out_struct.load_math_model_output(constants.results["TacticalMMInput"])
    out_struct.create_file(constants.output_path)
    return out_struct


def create_tactical_simulation(model):
    tac_input_file = TacticalSMInput(model)
    tac_input_file.create_tables()
    tac_input_file.create_file(constants.output_path)
    return tac_input_file


def create_tactical_math_model(model):
    tacmm = TacticalMMInput(model)
    tacmm.set_order_times([0.4, 0.2])
    tacmm.set_probabilities([0.1, 0.2, 0.4, 0.2, 0.1])
    tacmm.create_file(constants.output_path)
    return tacmm


if __name__ == "__main__":
    archive = create_archive()
    # archive = load_archive()
    # op_sm = create_operational_simulation(archive, "aralik")
    # create_tactical_simulation(archive)
    # op_mm = create_operational_math_model(archive, "aralik", 4)
    # tmm = create_tactical_math_model(archive)

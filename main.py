from backend.utils.file_dialog import *
from backend.compiler import *
from backend.analyzer import *
import eel

eel.init('frontend')
# Archive initialization
archive = None
archive_path = None
# Paths
result_path = None
analysis_dir = None
plan_path = None
second_plan_path = None
workdays_path = None
second_workdays_path = None
upper_model_output_path = None
# ---
new_file_paths = {x: None for x in ["bom", "times", "order", "machineInfo", "tbd"]}
summary_dir = None

output_dir = None

print('YnUgZMO8bnlhZGEgaXlpbGVyLCBrw7Z0w7xsZXIsIGludGlrYW0gc2F2YcWfxLEsIGJleWF6IG5pbmph')


@eel.expose
def open_url(file_name, size=(1200, 600)):
    eel.start(file_name, size=size, port=0)


########################################################################################################################
########################################################################################################################
#                                               TOOLS FOR ARCHIVAL                                                     #
########################################################################################################################
########################################################################################################################
@eel.expose
def get_archive_path():
    global archive_path
    archive_path = ask_file((("Archive Files", "*.mng"),))
    if archive_path is not None:
        archive_path = archive_path.name
        return "../" + "/".join(archive_path.split("/")[-2:])
    else:
        archive_path = None
        return 0


@eel.expose
def load_archive():
    global archive_path, archive
    if archive_path is not None:
        archive = revert_checkpoint(archive_path)
        print(archive)
        # open_url("index.html", size=(1200, 600))
    else:
        return 0


@eel.expose
def proceed_to_index():
    if archive is not None:
        return 1
    else:
        return 0


########################################################################################################################
########################################################################################################################
#                                           TOOLS FOR ARCHIVE UPDATE                                                   #
########################################################################################################################
########################################################################################################################
# noinspection PyUnresolvedReferences
@eel.expose
def update_archive(selected_file_types):
    global archive
    if "tbd" in selected_file_types:
        archive.update_tbd(new_file_paths["tbd"])
    elif "machineInfo" in selected_file_types:
        archive.update_machine_info(new_file_paths["machineInfo"])
    elif "bom" in selected_file_types:
        archive.update_bom(new_file_paths["bom"])
    elif "times" in selected_file_types:
        archive.update_times(new_file_paths["times"])
    elif "order" in selected_file_types:
        archive.update_orders(new_file_paths["order"])
    if ("bom" in selected_file_types) | ("times" in selected_file_types):
        archive.merge_files()


@eel.expose
def update_new_file_path(file_type):
    global new_file_paths
    new_file_paths[file_type] = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if new_file_paths[file_type] is not None:
        new_file_paths[file_type] = new_file_paths[file_type].name
        return "../" + "/".join(new_file_paths[file_type].split("/")[-2:])
    else:
        new_file_paths[file_type] = None
        return 0


########################################################################################################################
########################################################################################################################
#                                               TOOLS FOR ANALYSIS                                                     #
########################################################################################################################
########################################################################################################################
@eel.expose
def get_result_path(filetype):
    global result_path
    if filetype == "xl":
        result_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    elif filetype == "txt":
        result_path = ask_file((("Text Files", "*.txt"),))
    if result_path is not None:
        result_path = result_path.name
        return "../" + "/".join(result_path.split("/")[-2:])
    else:
        result_path = None
        return 0


@eel.expose
def get_result_analysis_dir():
    global analysis_dir
    analysis_dir = ask_directory()
    if analysis_dir != "":
        return "../" + analysis_dir.split("/")[-1] + "/"
    else:
        analysis_dir = None
        return 0


@eel.expose
def analyze_result(result_type):
    global result_path, analysis_dir
    try:
        if result_type == "tkpm":
            analyze_tkpm_results(result_path, analysis_dir)
        elif result_type == "okpm":
            analyze_okpm_results(result_path, analysis_dir)
        elif result_type == "okpb":
            analyze_okpb_results(result_path, analysis_dir)
        return 1
    except:
        return 0


########################################################################################################################
########################################################################################################################
#                                       TOOLS FOR INPUT FILE CREATION                                                  #
########################################################################################################################
########################################################################################################################

@eel.expose
def get_input_file_output_dir():
    global output_dir
    output_dir = ask_directory()
    if output_dir != "":
        output_dir += "/"
        return "../" + output_dir.split("/")[-2] + "/"
    else:
        output_dir = None
        return 0


@eel.expose
def get_plan():
    global plan_path
    plan_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if plan_path is not None:
        plan_path = plan_path.name
        return "../" + "/".join(plan_path.split("/")[-2:])
    else:
        plan_path = None
        return 0


@eel.expose
def get_second_plan():
    global second_plan_path
    second_plan_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if second_plan_path is not None:
        second_plan_path = second_plan_path.name
        return "../" + "/".join(second_plan_path.split("/")[-2:])
    else:
        second_plan_path = None
        return 0


@eel.expose
def get_workdays():
    global workdays_path
    workdays_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if workdays_path is not None:
        workdays_path = workdays_path.name
        return "../" + "/".join(workdays_path.split("/")[-2:])
    else:
        workdays_path = None
        return 0


@eel.expose
def get_second_workdays():
    global second_workdays_path
    second_workdays_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if second_workdays_path is not None:
        second_workdays_path = second_workdays_path.name
        return "../" + "/".join(second_workdays_path.split("/")[-2:])
    else:
        second_workdays_path = None
        return 0


@eel.expose
def get_upper_model_output():
    global upper_model_output_path
    upper_model_output_path = ask_file((("Excel Files", ("*.xlsx", "*.xls", "*.csv")),))
    if upper_model_output_path is not None:
        upper_model_output_path = upper_model_output_path.name
        return "../" + "/".join(upper_model_output_path.split("/")[-2:])
    else:
        upper_model_output_path = None
        return 0


@eel.expose
def create_input_file(input_type, *args):
    global plan_path, second_plan_path, workdays_path, second_workdays_path, output_dir, archive
    try:
        if input_type == "tkpm":
            eel.raiseForecastStartedAlert()
            input_file = TacticalMMInput(archive)
            eel.raiseForecastEndedAlert()
            input_file.set_order_times(args[0])
            input_file.set_probabilities(args[1])
            input_file.create_file(output_dir)
        elif input_type == "okpm":
            input_file = OperationalMMInput(archive, plan_path, args[0])
            input_file.load_days(workdays_path)
            input_file.load_math_model_output(upper_model_output_path)
            input_file.create_file(output_dir)
        elif input_type == "okpb":
            input_file = OperationalSMInput(archive)
            input_file.load_plan(plan_path)
            input_file.load_days(workdays_path)
            if args[0]:
                input_file.load_plan(plan_path)
            else:
                input_file.load_plan(second_plan_path)
                input_file.load_days(second_workdays_path)
            input_file.load_math_model_output(upper_model_output_path)
            input_file.create_tables()
            input_file.create_file(output_dir)
        eel.raiseInputCreationSuccessAlert()()
    except:
        eel.raiseCreationErrorJs()()


########################################################################################################################
########################################################################################################################
#                                          TOOLS FOR ARCHIVE CREATION                                                  #
########################################################################################################################
########################################################################################################################
@eel.expose
def create_archive():
    try:
        global archive, new_file_paths
        archive = ArchiveDatabase()
        archive.load_files_to_be_deleted(new_file_paths["tbd"])
        archive.load_machine_info(new_file_paths["machineInfo"])
        archive.load_bom(new_file_paths["bom"])
        archive.load_times(new_file_paths["times"])
        archive.order_history.add_orders(new_file_paths["order"])
        archive.merge_files()
        return 1
    except:
        return 0


@eel.expose
def logout_app():
    try:
        archive_dir = ask_directory()
        if archive_dir != "":
            archive.save_checkpoint(archive_dir + "/Archive.mng")
        return 1
    except:
        return 0


########################################################################################################################
########################################################################################################################
#                                          TOOLS FOR ARCHIVE CREATION                                                  #
########################################################################################################################
########################################################################################################################


@eel.expose
def get_summary_dir():
    global summary_dir
    summary_dir = ask_directory()
    if summary_dir != "":
        return "../" + summary_dir.split("/")[-1] + "/"
    else:
        summary_dir = None
        return 0


# noinspection PyUnresolvedReferences
@eel.expose
def create_summary(selected_file_types):
    global archive, summary_dir
    try:
        archive.create_summary(selected_file_types, summary_dir)
        return 1
    except:
        return 0



@eel.expose
def kill_app():
    exit(0)


@eel.expose
def get_from_js(data):
    global archive
    archive = data


if __name__ == "__main__":
    open_url("login.html", size=(1200, 600))

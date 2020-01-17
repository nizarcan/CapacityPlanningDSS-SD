from input_generator.app_backend import *
import input_generator.constants as constants

# BOM dosyasını okuma aşaması
bom_sheet_name = get_excel_sheet_names(constants.bom_path)
bom_sheet_name = bom_sheet_name[0]
bom_df = read_excel_sheet(constants.bom_path, name_of_sheet=bom_sheet_name)
bom_df = arrange_df(bom_df, [0, 3, 2, 5, 4], "bom", constants.tbd_path)

times_sheet_name = get_excel_sheet_names(constants.times_path)
times_sheet_name = times_sheet_name[0]
times_df = read_excel_sheet(constants.times_path, constants.times_sheet_name)
times_df = arrange_df(times_df, [3, 25, 29, 30], "times")

times_df["station"] = format_machine_names(times_df, "station")
merged_df = merge_times_and_bom(bom_df, times_df)

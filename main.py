from app_backend.data_process import *
import app_backend.constants as constants

# BOM dosyasını okuma aşaması
bom_sheet_name = get_excel_sheet_names(constants.bom_path)
bom_sheet_name = bom_sheet_name[0]
bom_df = read_excel_sheet(constants.bom_path, name_of_sheet=bom_sheet_name)
bom_df = arrange_df(bom_df, [0, 3, 2, 5, 4], "bom", constants.tbd_path)
bom_df = determine_amounts(bom_df)

legend_table = create_legend_table(bom_df)
input_table = create_input_table(bom_df)
duplication_table = create_duplication_table(bom_df)

times_sheet_name = get_excel_sheet_names(constants.times_path)
times_sheet_name = times_sheet_name[2]
times_df = read_excel_sheet(constants.times_path, constants.times_sheet_name)
times_df, montaj_df, cmy_df = arrange_df(times_df, [3, 25, 29, 30], "times")

merged_df = merge_bom_and_times(bom_df, times_df)

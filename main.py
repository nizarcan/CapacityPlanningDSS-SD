from app_backend.data_process import *
from app_backend.excel_operations import *
import app_backend.constants as constants

# BOM dosyasını okuma aşaması
bom_sheet_name = get_excel_sheet_names(constants.bom_path)
bom_sheet_name = bom_sheet_name[0]
bom_df = read_excel_sheet(constants.bom_path, name_of_sheet = bom_sheet_name)
bom_df = arrange_df(df = bom_df, relevant_col_idx = [0, 3, 2, 5, 4], df_type = "bom", tbd_path = constants.tbd_path)
bom_df = determine_amounts(bom_df)

times_sheet_name = get_excel_sheet_names(constants.times_path)
times_sheet_name = times_sheet_name[2]
times_df = read_excel_sheet(constants.times_path, constants.times_sheet_name)
times_df, montaj_df, cmy_df, set_list_df = arrange_df(df = times_df, relevant_col_idx = [3, 25, 29, 30],
                                                      df_type = "times")
merged_df = merge_bom_and_times(bom_df, times_df)
merged_df = arrange_df(df = merged_df, df_type = "merged", assembly_df = montaj_df)

legend_table = create_legend_table(bom_df)
input_table = create_input_table(bom_df)
duplication_table = create_duplication_table(bom_df)
sequence_table = sequence_type_matrix(df = merged_df, lookup_col = "station", matrix_type = "station")
time_table = sequence_type_matrix(df = merged_df, lookup_col = "cycle_times", matrix_type = "time")
join_matrix, join_amount_table = create_join_matrix(merged_df)
set_table = set_list_table(set_list_df)
order_table_df = order_table(input_table, 20)

create_excel_file(legend_table, input_table, sequence_table, time_table, join_matrix, join_amount_table,
                  duplication_table, set_table, order_table_df)

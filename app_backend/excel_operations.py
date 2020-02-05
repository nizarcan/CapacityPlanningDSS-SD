import pandas as pd
import win32com.client
from string import ascii_uppercase as auc
import app_backend.constants as constants


def create_excel_file(legend_df, input_df, sequence_df, time_df, join_df,
                      join_info_df, duplication_df, set_list_df, order_matrix_df):
    with pd.ExcelWriter(constants.output_path) as writer:
        legend_df.to_excel(writer, sheet_name = "LEGEND")
        input_df.to_excel(writer, sheet_name = "input_table")
        sequence_df.to_excel(writer, sheet_name = "sequence_matrix")
        time_df.to_excel(writer, sheet_name = "time_matrix")
        join_df.to_excel(writer, sheet_name = "join_matrix")
        join_info_df.to_excel(writer, sheet_name = "join_info")
        duplication_df.to_excel(writer, sheet_name = "product_duplication")
        set_list_df.to_excel(writer, sheet_name = "set_lists")
        order_matrix_df.to_excel(writer, sheet_name = "orders")
    excel_named_ranges(input_df, sequence_df, time_df, join_df, join_info_df, duplication_df, set_list_df,
                       order_matrix_df, constants.output_path)


def excel_named_ranges(input_df, sequence_df, time_df, join_df, join_info_df,
                       duplication_df, set_list_df, order_matrix_df, xl_file_path):
    xl = win32com.client.Dispatch('Excel.Application')

    info_dict = {
        "coordinate_matrix": {"sheet": "set_lists", "col_start": 5, "num_of_cols": 2,
                              "num_of_rows": set_list_df.shape[0]},
        "duplication_matrix": {"sheet": "product_duplication", "col_start": 3, "num_of_cols": 2,
                               "num_of_rows": duplication_df.shape[0]},
        "join_matrix": {"sheet": "join_matrix", "col_start": 2, "num_of_cols": join_df.shape[1],
                        "num_of_rows": join_df.shape[0]},
        "join_quantity": {"sheet": "join_info", "col_start": 3, "num_of_cols": 1, "num_of_rows": join_info_df.shape[0]},
        "order_matrix": {"sheet": "orders", "col_start": 2, "num_of_cols": 3, "num_of_rows": order_matrix_df.shape[0]},
        "part_quantity_list": {"sheet": "input_table", "col_start": 3, "num_of_cols": 1,
                               "num_of_rows": input_df.shape[0]},
        "queues_list": {"sheet": "set_lists", "col_start": 3, "num_of_cols": 1, "num_of_rows": set_list_df.shape[0]},
        "resources_list": {"sheet": "set_lists", "col_start": 4, "num_of_cols": 1, "num_of_rows": set_list_df.shape[0]},
        "sequence_matrix": {"sheet": "sequence_matrix", "col_start": 2, "num_of_cols": sequence_df.shape[1],
                            "num_of_rows": sequence_df.shape[0]},
        "stations_list": {"sheet": "set_lists", "col_start": 2, "num_of_cols": 1, "num_of_rows": set_list_df.shape[0]},
        "time_matrix": {"sheet": "time_matrix", "col_start": 2, "num_of_cols": time_df.shape[1],
                        "num_of_rows": time_df.shape[0]},
    }  # missing: setup_matrix, setups_list

    namerange = "={}!${}$2:${}${}"

    xl.Workbooks.Open(Filename = xl_file_path)
    for namerange_keys in info_dict.keys():
        xl.ActiveWorkbook.Names.Add(Name = namerange_keys, RefersTo = namerange.format(
            info_dict[namerange_keys]["sheet"],  # name of the named range
            auc[info_dict[namerange_keys]["col_start"] - 1],  # the letter that is going to be used for the start
            auc[info_dict[namerange_keys]["col_start"] + info_dict[namerange_keys]["num_of_cols"] - 2],  # letter of end
            info_dict[namerange_keys]["num_of_rows"] + 1))  # number of the ending column
    xl.Workbooks(1).Close(SaveChanges = 1)
    xl.Application.Quit()

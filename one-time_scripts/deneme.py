from app_backend.compiler import revert_checkpoint
import app_backend.constants as constants
from datetime import datetime
import pandas as pd

archive = revert_checkpoint(constants.archive_file_path)

df = pd.read_excel("C://sl_data//xlsx//okpm_results.xlsx", sheet_name = "A")
archive.load_machine_info(constants.machine_info_path)
machine_legend = pd.read_excel("C://sl_data//xlsx//okpm_results.xlsx", sheet_name = "machine_legend", header = 0,
                               index_col = 0)


def create_schedule(gunler, amount, shift, overtime_hour):
    temp_df = pd.DataFrame(columns = [0, 1])
    for x in range(len(gunler)):
        if conditionals[x] == 1:
            temp_df = pd.concat([temp_df, df_types[1][shift]], ignore_index = True)
        elif conditionals[x] == 2:
            temp_df = pd.concat([temp_df, df_types[2](overtime_hour)], ignore_index = True)
        else:
            temp_df = pd.concat([temp_df, df_types[3]], ignore_index = True)
    temp_df[0] = temp_df[0]*amount
    return temp_df


def ctesi_creator(hour):
    if hour < 24:
        out = pd.DataFrame(data = [[1, hour], [0, 24 - hour]])
    else:
        out = pd.DataFrame(data = [[1, 24], [0, 0]])
    return out


df_types = {1: {1: pd.DataFrame(data = [[1, 0, 0, 0, 0, 0], [7.5, 0.5]*3]).transpose(),
                2: pd.DataFrame(data = [[1, 0, 1, 0, 0, 0], [7.5, 0.5]*3]).transpose(),
                3: pd.DataFrame(data = [[1, 0, 1, 0, 1, 0], [7.5, 0.5]*3]).transpose()}, 2: ctesi_creator,
            3: pd.DataFrame(data = [0, 24]).transpose()}

gunler_list = [pd.to_datetime("2019.12", format = "%Y.%m") + pd.to_timedelta(str(x) + " days") for x in range(0, 31)]
aralik_gunler = pd.read_excel("C://sl_data//xlsx//aralik_gunler.xlsx")
aralik_gunler = aralik_gunler.iloc[:, 1:]
conditionals = [1 if (gunler_list[x].dayofweek < 5) & (aralik_gunler.iloc[:, x].values[0] == 1)
                else 2 if (gunler_list[x].dayofweek == 5) & (aralik_gunler.iloc[:,x].values[0] == 1)
                else 3 for x in range(0, len(gunler_list))]

a = {x: create_schedule(conditionals, archive.machine_info[archive.machine_info["machine"] == x]["quantity"].values[0],
                        archive.machine_info[archive.machine_info["machine"] == x]["shift"].values[0],
                        df[(df[df.columns[0]] == 2) & (df[df.columns[1]] == machine_legend[machine_legend["station"] == x].index.values[0])].iloc[:, 2:].sum(axis = 1).values[0]/sum([y == 2 for y in conditionals])) for x in machine_legend["station"]}

import backend.constants as constants
from datetime import datetime
import pandas as pd

df = pd.read_excel("C://sl_data//xlsx//okpm_results.xlsx", sheet_name="A")
archive.load_machine_info(constants.machine_info_path)
machine_legend = pd.read_excel("C://sl_data//xlsx//okpm_results.xlsx", sheet_name="machine_legend", header=0, index_col=0)
conditionals = [3, 1 ,1 ,1, 2, 3, 2, 1, 2, 3, 2]


def create_schedule(gunler, shift, overtime_hour):
    temp_df = pd.DataFrame(columns=[0,1])
    for x in range(len(gunler)):
        if conditionals[x] == 1:
            temp_df = pd.concat([temp_df, df_types[1][shift]], ignore_index = True)
        elif conditionals[x] == 2:
            temp_df = pd.concat([temp_df, df_types[2](overtime_hour)], ignore_index = True)
        else:
            temp_df = pd.concat([temp_df, df_types[3]], ignore_index = True)
    return temp_df


df_types = {1: {1: pd.DataFrame(data=[[1, 0, 0, 0, 0, 0], [7.5, 0.5]*3]).transpose(), 2: pd.DataFrame(data=[[1, 0, 1, 0, 0, 0], [7.5, 0.5]*3]).transpose(), 3: pd.DataFrame(data=[[1, 0, 1, 0, 1, 0], [7.5, 0.5]*3]).transpose()}, 2: ctesi_creator, 3: pd.DataFrame(data=[0, 24]).transpose()}


def ctesi_creator(hour):
    if hour<24:
        out = pd.DataFrame(data=[[1,hour],[0, 24-hour]])
    else:
        out = pd.DataFrame(data=[[1,24],[0, 0]])
    return out

gunler_list = [pd.to_datetime("2019.12", format="%Y.%m") + pd.to_timedelta(str(x) + " days") for x in range(0, 31)]
conditionals = [1 if (gunler_list[x].dayofweek<5) & (aralik_gunler.iloc[:, x].values[0]==1) else 2 if (gunler_list[x].dayofweek==5) & (aralik_gunler.iloc[:, x].values[0]==1) else 3 for x in range(0, len(gunler_list))]
aralik_gunler = pd.read_excel("C://sl_data//xlsx//aralik_gunler.xlsx")

aralik_gunler = aralik_gunler.iloc[:, 1:]

a = {archive.machine_info[archive.machine_info["machine"] == x]["machine"]: create_schedule(conditionals, archive.machine_info[archive.machine_info["machine"] == x]["shift"], df[(df[df.columns[0]]==2) & (df[df.columns[1]]==machine_legend.iloc[archive.machine_info[archive.machine_info["machine"] == x].index.tolist()[0]])].values[0]) for x in archive.machine_info["machine"]}

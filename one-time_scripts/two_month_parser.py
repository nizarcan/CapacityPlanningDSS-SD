import pandas as pd
from openpyxl import load_workbook
from backend.utils.xl_ops import get_excel_sheet_names
import datetime


file_dir = "D:\\Nizar\\Desktop\\AYLIK_PLAN-2019.xlsx"

plan_sheets = get_excel_sheet_names(file_dir)
wb = load_workbook(file_dir, read_only = True)
bant_list = [str(x) + ". Bant" for x in range(1, 5)] + ["LOOP"]
assembly_unit_dict = {"1. Bant": "BANT", "2. Bant": "BANT", "3. Bant": "BANT", "4. Bant": "BANT", "LOOP": "LOOP"}
whole_dataframe = pd.DataFrame()
for sheet in plan_sheets[:-8]:
    plan = pd.DataFrame(wb[sheet].values)
    plan.columns = plan.iloc[5]
    plan.drop(plan[~plan["TARİH"].apply(lambda x: type(x) == datetime.datetime)].index, inplace = True)
    plan = plan[["ÜRÜNKODU", "TARİH", "PLANLANANÜRE.MİK.", "P.T"]]
    plan.columns = ["product_no", "start_date", "amount", "due_date"]
    whole_dataframe = whole_dataframe.append(plan)

for sheet in plan_sheets[-8:]:
    plan = pd.DataFrame(wb[sheet].values)
    plan.columns = plan.iloc[2]
    plan.drop(plan[~pd.Series([x in bant_list for x in plan[plan.columns[0]]])].index, inplace = True)
    plan = plan[["ÜRÜNKODU", "Tarih", "PLAN ADET", "TERMİN"]]
    plan.columns = ["product_no", "start_date", "amount", "due_date"]
    whole_dataframe = whole_dataframe.append(plan)

whole_dataframe.drop(whole_dataframe[~whole_dataframe.due_date.apply(lambda x: type(x) == datetime.datetime)].index, inplace=True)
whole_dataframe.reset_index(inplace=True, drop=True)
month_list = ["ocak", "subat", "mart", "nisan", "mayis", "haziran", "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"]
month_dict = {x: month_list[x-1] for x in range(1, 13)}
for month in month_dict.keys():
    if whole_dataframe[whole_dataframe.start_date.apply(lambda x: x.month) == month].shape[0] == 0:
        pass
    else:
        whole_dataframe[whole_dataframe.start_date.apply(lambda x: x.month) == month].to_excel("C:\\sl_data\\planlar\\"+month_dict[month] + "_plan.xlsx")


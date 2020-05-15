from datetime import datetime
import pandas as pd

subat_plan = pd.read_excel("C://sl_data//xlsx//planlar.xlsx", sheet_name='ŞubatPlan')
subat_plan = subat_plan[subat_plan.columns[[0, 1, 3, 4, 6]]]
subat_plan = subat_plan.groupby(by=["Tarih", subat_plan.columns[2], subat_plan.columns[3]], as_index=False).agg({"PLAN ADET": "sum"})
subat_gunler = pd.read_excel("C://sl_data//xlsx//subat_gunler.xlsx", header=0, index_col=0)
current_month = datetime(subat_plan.Tarih.dt.year.mode(), subat_plan.Tarih.dt.month.mode(), 1).date()

subat_mat_availability = [1 if (list(subat_gunler.values)[0][x] == 1) & ((current_month+pd.to_timedelta(x, unit="d")).weekday()<5) else 0 for x in range(0, subat_gunler.columns.max())]

replace_dict = {}
if current_month.weekday()>=5:
    replace_dict[current_month] = pd.to_datetime((current_month + pd.to_timedelta(7 - current_month.weekday(), unit="d"))).date()
else:
    replace_dict[current_month] = current_month
for x in range(1, subat_gunler.columns.max()):
    if subat_mat_availability[x] == 1:
        replace_dict[(current_month+pd.to_timedelta(x, unit="d"))] = pd.to_datetime(current_month + pd.to_timedelta(x, unit = "d")).date()
    else:
        replace_dict[(current_month+pd.to_timedelta(x, unit="d"))] = pd.to_datetime(max(replace_dict.values())).date()


renewed_dict = {x.day: replace_dict[x].day for x in replace_dict}
subat_plan["gun"] = subat_plan["Tarih"].dt.day
subat_plan.gun.replace(renewed_dict, inplace=True)
subat_plan = subat_plan.groupby(by=["gun", subat_plan.columns[2]], as_index=False).agg({"PLAN ADET": "sum"})
our_plan = subat_plan.pivot(subat_plan.columns[1], "gun", "PLAN ADET").fillna(0)
# subat_plan["Tarih"] = subat_plan["Tarih"].dt.date
# subat_plan["Tarih"].replace(replace_dict, inplace=True)

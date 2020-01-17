from app_backend import *

# BOM dosyasını okuma aşaması
bom_df = read_excel_sheet("test_app/bom.xlsx", "2100 Sonrası BOM")
bom_df = arrange_df(bom_df, [0, 3, 2, 5, 4], "bom", "test_app/silinecekler.xlsx")

times_df = read_excel_sheet("test_app/times.xlsx", "DÜZLİST")
times_df = arrange_df(times_df, [3, 25, 29, 30], "times")
times_df["station"] = format_machine_names(times_df, "station")
merged_df = merge_times_and_bom(bom_df, times_df)
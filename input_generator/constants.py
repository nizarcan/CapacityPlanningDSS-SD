"""
TC MANGO
Systems Design Project Constants & File Paths
"""

bom_path = "C:/sl_data/bom.xlsx"
bom_sheet_name = "2100 Sonrası BOM"
times_path = "C:/sl_data/times.xlsx"
times_sheet_name = "DÜZLİST"
tbd_path = "C:/sl_data/tbd.xlsx"
output_path = "C:/sl_data/input_file.xlsx"

start = times()
wb = load_workbook(filename = constants.bom_path, read_only= True)
sheet = wb[wb.sheetnames[0]]
df = DataFrame(sheet.values)
df.columns = df.iloc[0, :]
df = df.drop(0)
end = times()
delta = end - start
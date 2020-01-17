











relevant_col_idx = [0, 3, 2, 5, 4]
bom_df["Seviye"] = [int(x[-1]) for x in bom_df[bom_df.columns[relevant_col_idx][2]]]
relevant_col_idx[2] = len(bom_df.columns)-1
relevant_col_names = bom_df.columns[relevant_col_idx]
cols_to_drop = bom_df.columns[list(set(range(len(bom_df.columns))) - set(relevant_col_idx))]
bom_df.drop(cols_to_drop, axis=1, inplace=True)
bom_df = bom_df.reindex(columns=relevant_col_names)
bom_df.columns = ["product_no", "part_no", "level", "amount", "explanation"]
# s = (bom_df[bom_df.columns[2]].ne(bom_df[bom_df.columns[2]].shift(1, fill_value=1)) |
# bom_df[bom_df.columns[2]].ne(1)).cumsum()
# bom_df = bom_df.groupby(s).tail(1)
if bom_df.at[bom_df.index[-1], bom_df.columns[2]] == 1:
    bom_df.drop(bom_df.index[-1], inplace = True)
bom_df.reset_index(drop = "index", inplace = True)

items_to_delete = pd.read_excel("test_app/silinecekler.xlsx")
s = [str(x).split(".")[0] not in list(items_to_delete["Kalacaklar"]) for x in bom_df["part_no"]]
bom_df = bom_df.drop(np.where(np.asarray(s))[0])
s = (bom_df[bom_df.columns[2]].ne(bom_df[bom_df.columns[2]].shift(1, fill_value=1)) | bom_df[bom_df.columns[2]].ne(1)).cumsum()
bom_df = bom_df.groupby(s).tail(1)

# Süre dosyasını okuma aşaması
times_df = pd.read_excel("test_app/times.xlsx", sheet_name="DÜZLİST")
# relevant_columns = ["Malzeme", "Hat-Makina", "cycle_time", "Hazırlık Süresi"]
relevant_col_idx = [3, 25, 29, 30]
relevant_col_names = times_df.columns[relevant_col_idx]
cols_to_drop = times_df.columns[list(set(range(len(times_df.columns))) - set(relevant_col_idx))]
times_df.drop(cols_to_drop, axis=1, inplace=True)
times_df = times_df.reindex(columns=relevant_col_names)
times_df.columns = ["part_no", "station", "cycle_times", "prep_times"]
times_df = times_df.groupby(["part_no", "station"], as_index=False).agg({"cycle_times": sum, "prep_times": max})
times_df[["prep_times", "cycle_times"]] = times_df[["prep_times", "cycle_times"]].fillna(0)

merged_df = pd.merge(left=bom_df, right=times_df, how="left", on="part_no")
merged_df = merged_df.reindex(columns=list(merged_df.columns[0:4]) + list(merged_df.columns[5:]) + list(merged_df.columns[4:5]))
merged_df["station"] = level_lookup(merged_df, "level", "station")
merged_df["times"] = level_lookup(merged_df, "level", "times")

s = (~(merged_df["station"].isnull() & merged_df["station"].shift(-1).isnull())).cumsum()
merged_revised = merged_df.copy()
merged_revised = merged_revised.groupby(s).head(1)
merged_revised.reset_index(drop="index", inplace=True)
del bom_df, cols_to_drop, merged_df, relevant_col_idx, relevant_col_names, s, times_df

a = list(set([x[:6] for x in merged_revised["product_no"]]))
a.sort()

# Inputların çekilmesi
s = bom_df[bom_df.columns[3]].ge(bom_df[bom_df.columns[3]].shift(-1, fill_value=1)).cumsum()
bom_inputs = bom_df.groupby(s).head(1)
for row in [bom_inputs.index[-1], bom_inputs.index[0]]:
    if bom_inputs.at[row, bom_inputs.columns[3]] == 1:
        bom_inputs.drop(row, inplace = True)

# Gereksiz seviye 1 ler çıkıyor
s = (df['Seviye'].ne(df['Seviye'].shift()) | df.Seviye.ne(1)).cumsum()
df = df.groupby(s).tail(1)
# Inputlar bulunuyor
s = df['Seviye'].ge(df['Seviye'].shift(-1, fill_value=1)).cumsum()
df = df.groupby(s).head(1)
for row in [df.index[-1], df.index[0]]:
    if df.at[row, "Seviye"] == 1:
        df.drop(row, inplace = True)


bom_df["new_amount"] = 1
bom_row = 0
while bom_row < len(bom_df):
    if (bom_df.loc[bom_row, "amount"] % 1 == 0) and (bom_df.loc[bom_row, "amount"] != 1):
        starting_amount = bom_df.loc[bom_row, "amount"]
        bom_df.loc[bom_row, "new_amount"] = starting_amount
        starting_level = bom_df.loc[bom_row, "level"]
        while bom_row < len(bom_df):
            bom_row += 1
            if bom_df.at[bom_row, "level"] > starting_level:
                bom_df.at[bom_row, "new_amount"] = starting_amount
            else:
                break
    bom_row += 1
bom_df['amount'] = bom_df['new_amount']
bom_df.drop('new_amount', axis = 1, inplace = True)
bom_df.reset_index(drop = "index", inplace = True)

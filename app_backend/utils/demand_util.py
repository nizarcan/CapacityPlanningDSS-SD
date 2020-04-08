import pandas as pd


def demand_parser(pivot=True, agg=True):
    df1 = pd.read_csv("C://sl_data//2100_tuketim.csv")
    df2 = pd.read_csv("C://sl_data//2200_tuketim.csv")
    df3 = pd.read_csv("C://sl_data//2019_kalan_tuketim.csv")
    df1 = df1[["Grş.trh.", "Malzeme", "Miktar"]].copy()
    df2 = df2[["Grş.trh.", "Malzeme", "Miktar"]].copy()
    df3 = df3[["Grş.trh.", "Malzeme", "Miktar"]].copy()
    df1.columns = ["date", "product_no", "amount"]
    df2.columns = ["date", "product_no", "amount"]
    df3.columns = ["date", "product_no", "amount"]
    df1.drop(df1[pd.to_numeric(df1.amount, errors="coerce").isna()].index, inplace=True)
    df1.reset_index(drop=True, inplace=True)
    df2.drop(df2[pd.to_numeric(df2.amount, errors="coerce").isna()].index, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    df3.drop(df3[pd.to_numeric(df3.amount, errors="coerce").isna()].index, inplace=True)
    df3.reset_index(drop=True, inplace=True)
    df1year = df1.date.str.split("/").apply(lambda x: x[2])
    df1month = df1.date.str.split("/").apply(lambda x: x[1])
    df1.drop(df1[(df1year == "2019") & (df1month == "09")].index, inplace = True)
    total_data = pd.concat([df1, df2, df3], ignore_index=True)
    total_data.date = pd.to_datetime(total_data.date, format="%d/%m/%Y")
    total_data.date = total_data.date.dt.strftime("%Y-%m")
    total_data.amount = total_data.amount.astype(int)
    total_data.product_no = total_data.product_no.astype(str)
    total_data = total_data.groupby(by=["product_no", "date"], as_index=False).agg({"amount": sum})
    total_data.drop(total_data[total_data.product_no.map(len) != 13].index, inplace=True)
    total_data.reset_index(drop=True, inplace=True)
    total_data.sort_values(by=["product_no", "date"], ascending=True, inplace=True)
    history_pivot = total_data.copy()
    if agg & pivot:
        history_pivot["product_family"] = history_pivot.product_no.str.split(".").apply(lambda x: x[0])
        history_pivot = history_pivot.groupby(by = ["product_family", "date"],
                                              as_index = False).agg({"amount": sum})
        history_pivot = history_pivot.pivot(index="product_family", columns="date", values="amount").fillna(0)
    elif pivot:
        history_pivot = history_pivot.pivot(index="product_no", columns="date", values="amount").fillna(0)
    elif agg:
        history_pivot["product_family"] = history_pivot.product_no.str.split(".").apply(lambda x: x[0])
        history_pivot = history_pivot.groupby(by = ["product_family", "date"], as_index = False).agg({"amount": sum})
    return history_pivot


if __name__ == "__main__":
    demand_data = demand_parser(pivot = True, agg = True)
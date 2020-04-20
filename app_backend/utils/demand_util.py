import pandas as pd


def extract_forecast(orders: pd.DataFrame):
    df = orders.iloc[:, -12:].copy()
    df.drop(df[df.sum(axis=1) == 0].index, inplace=True)
    return df


class OrderHistory:
    def __init__(self):
        self.orders = None

    def initialize(self):
        df1 = pd.read_csv("C://sl_data//2100_tuketim.csv", low_memory=False)
        df2 = pd.read_csv("C://sl_data//2200_tuketim.csv", low_memory=False)
        df3 = pd.read_csv("C://sl_data//2019_kalan_tuketim.csv", low_memory=False)
        df1 = df1[["Grş.trh.", "Malzeme", "Miktar"]].copy()
        df2 = df2[["Grş.trh.", "Malzeme", "Miktar"]].copy()
        df3 = df3[["Grş.trh.", "Malzeme", "Miktar"]].copy()
        df1.columns = ["date", "product_no", "amount"]
        df2.columns = ["date", "product_no", "amount"]
        df3.columns = ["date", "product_no", "amount"]
        df1.drop(df1[pd.to_numeric(df1.amount, errors = "coerce").isna()].index, inplace = True)
        df1.reset_index(drop = True, inplace = True)
        df2.drop(df2[pd.to_numeric(df2.amount, errors = "coerce").isna()].index, inplace = True)
        df2.reset_index(drop = True, inplace = True)
        df3.drop(df3[pd.to_numeric(df3.amount, errors = "coerce").isna()].index, inplace = True)
        df3.reset_index(drop = True, inplace = True)
        df1year = df1.date.str.split("/").apply(lambda x: x[2])
        df1month = df1.date.str.split("/").apply(lambda x: x[1])
        df1.drop(df1[(df1year == "2019") & (df1month == "09")].index, inplace = True)
        total_data = pd.concat([df1, df2, df3], ignore_index = True)
        total_data.date = pd.to_datetime(total_data.date, format = "%d/%m/%Y")
        total_data.date = total_data.date.dt.strftime("%Y-%m")
        total_data.amount = total_data.amount.astype(int)
        total_data.product_no = total_data.product_no.astype(str)
        total_data = total_data.groupby(by = ["product_no", "date"], as_index = False).agg({"amount": sum})
        total_data.drop(total_data[total_data.product_no.map(len) != 13].index, inplace = True)
        total_data.sort_values(by = ["date", "product_no"], ascending = True, inplace = True)
        total_data.reset_index(drop = True, inplace = True)
        self.orders = total_data.copy()

    def agg(self, pivot: bool = True):
        data = self.orders.copy()
        data["product_family"] = data.product_no.str.split(".").apply(lambda x: x[0])
        data = data.groupby(by = ["product_family", "date"], as_index = False).agg({"amount": sum})
        if pivot:
            data = data.pivot(index = "product_family", columns = "date", values = "amount").fillna(0)
        return data

    def pivot(self):
        data = self.orders.copy()
        data = data.pivot(index = "product_no", columns = "date", values = "amount").fillna(0)
        return data

    def add_orders(self, file_dir):
        new_data = None
        if (file_dir.split(".")[-1] == "xlsx") | (file_dir.split(".")[-1] == "xls"):
            new_data = pd.read_excel(file_dir)
        elif file_dir.split(".")[-1] == "csv":
            new_data = pd.read_csv(file_dir, low_memory=False)
        if new_data is None:
            return 0
        new_data = new_data[["Grş.trh.", "Malzeme", "Miktar"]].copy()
        new_data.columns = ["date", "product_no", "amount"]
        new_data.drop(new_data[pd.to_numeric(new_data.amount, errors = "coerce").isna()].index, inplace = True)
        new_data.drop(new_data[new_data.product_no.map(len) != 13].index, inplace = True)
        new_data.date = pd.to_datetime(new_data.date, format = "%d/%m/%Y")
        new_data.date = new_data.date.dt.strftime("%Y-%m")
        new_data.amount = new_data.amount.astype(int)
        new_data.product_no = new_data.product_no.astype(str)
        concat_data = pd.concat([self.orders, new_data], ignore_index = True)
        concat_data.sort_values(by = ["date", "product_no"], ascending = True, inplace = True)
        concat_data.reset_index(drop = True, inplace = True)
        self.orders = concat_data


if __name__ == "__main__":
    demand_data = OrderHistory()
    # demand_data.initialize()
    # pivoted_orders = demand_data.agg(pivot=True)

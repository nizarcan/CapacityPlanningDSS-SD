from app_backend.compiler import revert_checkpoint, TacticalMMInput, OperationalMMInput
import app_backend.constants as constants

archive = revert_checkpoint(constants.archive_file_path)
tmm = TacticalMMInput(archive, "a")
tmm.cross_trim()
a = archive.order_history.orders.copy()
a["product_family"] = a.product_no.str.split(".").apply(lambda x: x[0])
b = a.groupby("product_family", as_index=False).agg({"product_no": "count", "amount": "sum"})
b["order_amount"] = b.amount / b.product_no
b.order_amount = b.order_amount.floordiv(1)+1
b.drop(["product_no", "amount"], axis=1, inplace=True)
b.reset_index(inplace=True, drop=True)
b.to_excel("order_averages.xlsx")


c = archive.order_history.orders.copy()
d = c.groupby("product_no", as_index=False).agg({"date": "count", "amount": "sum"})
d["order_amount"] = d.amount / d.date
d.order_amount = d.order_amount.floordiv(1)+1
d.drop(["product_no", "amount"], axis=1, inplace=True)
omm = OperationalMMInput(archive, constants.aralik_order_path)
omm.cross_trim()
d.drop(d[~d.product_no.isin(omm.plan.product_no)].index, inplace=True)
d.reset_index(inplace=True, drop=True)
d.drop(["date", "amount"], inplace=True, axis=1)
d.to_excel("order_averages_aralik.xlsx")

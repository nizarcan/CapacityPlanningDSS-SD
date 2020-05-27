from backend.compiler import revert_checkpoint
from matplotlib import pyplot as plt
import backend.constants as constants


def load_archive():
    return revert_checkpoint(constants.archive_file_path)


if __name__ == "__main__":
    archive = load_archive()
    orders = archive.order_history.orders.copy()
    # orders = orders[orders.date > "2017"]
    orders["year"] = orders.date.str.split("-").apply(lambda x: x[0])
    order_data = {str(x): None for x in range(1, 13)}
    order_averages = {str(x): None for x in range(1, 13)}
    for month in order_data.keys():
        order_data[month] = orders[orders.date.str.split("-").apply(lambda x: x[1]) == ("0" + month)[-2:]]
        order_averages[month] = orders[orders.date.str.split("-").apply(lambda x: x[1]) == ("0" + month)[-2:]].groupby("year", as_index=False).agg({"amount": "sum"})
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(order_averages[month].year, order_averages[month].amount)
        ax.plot(order_averages[month].year, [order_averages[month].amount.mean()]*5)
        ax.set_title(month)
        ax.set_ylim(bottom=30000, top=125000)
        fig.savefig(month+".png")
        del fig, ax
    std = {str(x): order_averages[str(x)].amount.std() for x in range(1, 13)}

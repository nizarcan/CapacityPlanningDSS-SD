from statsmodels.tsa.holtwinters import ExponentialSmoothing
from dateutil.relativedelta import relativedelta
import pandas as pd


def predict_next_12_months(data):
    pred = pd.DataFrame()
    start_and_finish = [max(pd.to_datetime(data.columns, format = "%Y-%m")) + relativedelta(months=(x*11)+1) for x in range(2)]
    for prod_family in data.index:
        ts = data.loc[prod_family, :]
        ts.index = pd.DatetimeIndex(pd.to_datetime(ts.index, format = "%Y-%m"))
        ts.index.freq = "MS"
        try:
            model = ExponentialSmoothing(ts, trend = 'mul', seasonal = 'mul', seasonal_periods = 12).fit(
                use_basinhopping = True)
        except ValueError:
            model = ExponentialSmoothing(ts, trend = 'add', seasonal = 'add', seasonal_periods = 12).fit(
                use_basinhopping = True)
        except Warning:
            model = ExponentialSmoothing(ts, seasonal_periods = 12).fit()

        temp_pred = model.predict(start = start_and_finish[0], end = start_and_finish[1])
        pred[prod_family] = temp_pred

    pred = pred.transpose().floordiv(1).fillna(0)
    pred[pred < 0] = 0
    pred.columns = [x.strftime("%Y-%m") for x in pred.columns]
    return pred


if __name__=="__main__":
    from app_backend.compiler import revert_checkpoint

    archive = revert_checkpoint("C://sl_data//input//Archive.mng")
    forecast = predict_next_12_months(archive.order_history.agg(pivot=True).iloc[:, :-12])
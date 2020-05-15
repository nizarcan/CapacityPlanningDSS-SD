from app_backend.compiler import revert_checkpoint, TacticalMMInput
import app_backend.constants as constants


archive = revert_checkpoint(constants.archive_file_path)
tmm = TacticalMMInput(archive, archive.order_history.orders.iloc[:, -12:])
tmm.cross_trim()
temp_forecast = tmm.forecast.copy()
temp_forecast.drop(temp_forecast[temp_forecast.sum(axis = 1) == 0].index, inplace = True)
forecast_index = temp_forecast.index
temp_forecast = temp_forecast.reindex(temp_forecast.index.repeat(3))
temp_forecast.reset_index(inplace = True)
temp_forecast.iloc[::5, -12:] = temp_forecast.iloc[::5, -12:].sub(temp_forecast.iloc[::5, -12:].std(axis = 1)*1,
                                                                  axis = 0)
temp_forecast.iloc[1::5, -12:] = temp_forecast.iloc[1::5, -12:].sub(temp_forecast.iloc[1::5, -12:].std(axis = 1)*0.5,
                                                                    axis = 0)
temp_forecast.iloc[3::5, -12:] = temp_forecast.iloc[3::5, -12:].add(temp_forecast.iloc[3::5, -12:].std(axis = 1)*0.5,
                                                                    axis = 0)
temp_forecast.iloc[4::5, -12:] = temp_forecast.iloc[4::5, -12:].add(temp_forecast.iloc[4::5, -12:].std(axis = 1)*1,
                                                                    axis = 0)
num_forecast = temp_forecast._get_numeric_data()
num_forecast[num_forecast < 0] = 0
num_forecast.astype(int)
temp_forecast.iloc[:, -12:] = num_forecast
temp_forecast["new_index"] = [1, 2, 3, 4, 5]*forecast_index.nunique()
temp_forecast.set_index(keys = [temp_forecast.columns[0], "new_index"], inplace = True)
temp_forecast.index.names = ["", ""]

temp_forecast.to_excel("2sigma.xlsx", merge_cells=False, index_label=False)

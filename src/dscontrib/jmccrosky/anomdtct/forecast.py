# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import pandas as pd
from fbprophet import Prophet
from dscontrib.jmccrosky.forecast.utils import s2d

# The only holidays we have identified the need to explicitly model are Chinese
# New Year and Holi
chinese_new_year = pd.DataFrame({
    'ds': [
        s2d("2016-02-08"), s2d("2017-01-28"), s2d("2018-02-16"),
        s2d("2019-02-05"), s2d("2020-01-25")
    ],
    'holiday': "chinese_new_year",
    'lower_window': -20,
    'upper_window': 20,
})


holi = pd.DataFrame({
    'ds': [
        s2d("2016-03-06"), s2d("2017-03-13"), s2d("2018-03-02"),
        s2d("2019-03-21"), s2d("2020-03-10")
    ],
    'holiday': "holi",
    'lower_window': -1,
    'upper_window': 1,
})


def forecast(training_data, all_data):
    forecast = {}
    for c in all_data.keys():
        if (len(training_data) < 600):
            continue
        print("Starting with {}".format(c))
        # We use a mostly "default" model as we find it to be highly robust and
        # do not have resources to individually model each geo.  The only
        # adjustments made are the holidays sspecified and multiplicative
        # seasonality that is more appropriate, especially for regions in which
        # Firefox usage has grown from near-zero in our training period.
        model = Prophet(
            holidays=pd.concat([chinese_new_year, holi], ignore_index=True),
            seasonality_mode='multiplicative'
        )
        model.fit(training_data[c])
        forecast_period = model.make_future_dataframe(
            periods=(all_data[c].ds.max() - training_data[c].ds.max()).days,
            include_history=False
        )
        if (len(forecast_period) < 10):
            continue
        forecast[c] = model.predict(forecast_period)
        forecast[c]['ds'] = pd.to_datetime(forecast[c]['ds']).dt.date
        forecast[c] = forecast[c][["ds", "yhat", "yhat_lower", "yhat_upper"]]
        # We join the forecast with our full data to allow calculation of deviations.
        forecast[c] = forecast[c].merge(all_data[c], on="ds", how="inner")
        forecast[c]["delta"] = (forecast[c].y - forecast[c].yhat) / forecast[c].y
        forecast[c]["ci_delta"] = 0
        forecast[c].loc[
            forecast[c].delta > 0, "ci_delta"
        ] = (
            forecast[c].y - forecast[c].yhat
        ) / (
            forecast[c].yhat_upper - forecast[c].yhat
        )
        forecast[c].loc[
            forecast[c].delta < 0, "ci_delta"
        ] = (
            forecast[c].y - forecast[c].yhat
        ) / (
            forecast[c].yhat - forecast[c].yhat_lower
        )
        # We allow other fields to be returned here for testing and suppress
        # before publication
        # forecast[c] = forecast[c][["ds", "geo", "delta", "ci_delta"]]
        print("Done with {}".format(c))
    return forecast

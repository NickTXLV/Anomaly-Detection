# Anomaly Detection
Currently, we have an issue with over forecasting created by inconsistent inputs that are used to develop the forecast. When this happens, we see a daily forecast that should be around 20 units go to 500 units+. Most of these forecast outliers or anomalies, are discovered after they already have happened, creating inefficiencies.

The goal of the script is to flag outliers using simple moving averages to identify the difference in the daily forecast vs the moving averages. If the change is over a 50% threshold, then it is flagged as an outlier in the output file.

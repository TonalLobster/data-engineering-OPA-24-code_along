# ========================= #
#                           #
#                           #
#           Set up          #
#                           #
#                           #
# ========================= #


import dagster as dg
import pandas as pd
import matplotlib.pyplot as plt


# ========================= #
#                           #
#                           #
#           Asset           #
#                           #
#                           #
# ========================= #

# use decorator to create dagster asset
@dg.asset
def csv_data():
    df = pd.read_csv("data\sample_data.csv")
    return df

# use decorator to create dagster asset
@dg.asset
def age_plot(csv_data: pd.DataFrame):
    plt.figure(figsize=(8, 6))
    plt.hist(csv_data["age"], bins=20, color="skyblue", edgecolor="black")
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Count")
    plot_path = "age_distribution.png"
    plt.savefig(plot_path)




# ========================= #
#                           #
#                           #
#           Job             #
#                           #
#                           #
# ========================= #

csv_data_job = dg.define_asset_job(name= "csv_data_job", selection=[csv_data])
age_plot_job = dg.define_asset_job(name= "age_plot_job", selection=[age_plot])


# ========================= #
#                           #
#                           #
#         Schedule          #
#                           #
#                           #
# ========================= #

csv_data_schedule = dg.ScheduleDefinition(
    job=csv_data_job,
    cron_schedule="30 9 * * *" #UTC vs currently we have CEST in Sweden
)

# ========================= #
#                           #
#                           #
#         Sensor            #
#                           #
#                           #
# ========================= #

# In the decorator, we need to provide which asset to be monitored and which job to be triggered
@dg.asset_sensor(asset_key=dg.AssetKey("csv_data"),
                 job_name="age_plot_job")

# In the original function, we need to provide wich action this sensor should do when triggered
def age_plot_sensor():
    yield dg.RunRequest()

# ========================= #
#                           #
#                           #
#        Definitions        #
#                           #
#                           #
# ========================= #

# Tell dagster about the assets/other components that make up the pipline by
# passing them to  the 'Definitions' object
# This Definition object allows dagster to manage the assets execution and dependencies

defs = dg.Definitions(
                        assets=[csv_data, age_plot],
                        jobs=[csv_data_job, age_plot_job],
                        schedules=[csv_data_schedule],
                        sensors=[age_plot_sensor],
                    
)
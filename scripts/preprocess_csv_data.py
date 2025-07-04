import pandas as pd
import os

data = pd.read_csv("data/standby_data.csv")

departure_date = data["Departure Date"]
departure_time = data["Departure Time"]
record_date = data["Record Date"]
record_time = data["Record Time"]


departure_datetime = pd.to_datetime(
  departure_date + " " + departure_time,
  # format="%m/%d/%Y %I:%M%p"
  format="mixed",
  dayfirst=False
)
record_datetime = pd.to_datetime(
  record_date + " " + record_time,
  format="%m/%d/%Y %H:%M"
)

cleaned_data = pd.DataFrame({
"departure_datetime": departure_datetime,
"record_datetime": record_datetime,
"origin": data["Origin"],
"destination": data["Destination"],
"available_seats": data["Available Seats"],
"standby_count": data["Standby"],
"total_capacity": data["Capacity"],
})

cleaned_data.to_csv(f"data/cleaned_standby_data_{len(cleaned_data)}.csv", index=False)
print("done")
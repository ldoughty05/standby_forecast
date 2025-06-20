import pandas as pd
try:
  already_loaded_lines_count = pd.read_csv("cleaned_standby_data.csv").shape[0]
  data = pd.read_csv("standby_data.csv", skiprows=range(1, already_loaded_lines_count + 1))
except:
  data = pd.read_csv("standby_data.csv")



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

cleaned_data.to_csv("cleaned_standby_data.csv", index=False)
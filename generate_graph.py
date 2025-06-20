import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import argparse

parser = argparse.ArgumentParser(description="Plot standby availability over time")
parser.add_argument("--flight-id", type=int, required=True, help="ID of the flight in the database")
args = parser.parse_args()
flight_id = args.flight_id

db_connection = psycopg2.connect(
  dbname="standby_data",
  user="postgres",
  password="9476",
  # host="localhost"
)

query = """
SELECT
  r.record_datetime,
  f.scheduled_departure_datetime,
  EXTRACT(EPOCH FROM (f.scheduled_departure_datetime - r.record_datetime)) AS hours_before_departure,
  r.seats_available
FROM readings r
JOIN flights f ON r.flight_id = f.id
WHERE r.flight_id = %s
ORDER BY r.record_datetime;
"""

data = pd.read_sql(query, db_connection, params=(flight_id,))
db_connection.close()

plt.figure(figsize=(10, 5))
plt.plot(data["hours_before_departure"], data["seats_available"], marker='o')
plt.gca().invert_xaxis()
plt.title(f"Seat Availability Over Time (Flight ID {flight_id})")
plt.xlabel("Hours Before Departure")
plt.ylabel("Available Seats")
plt.grid(True)
plt.tight_layout()
plt.show()
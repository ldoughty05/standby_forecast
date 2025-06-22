import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
# from sqlalchemy import create_engine
import argparse
import os

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DEFAULT_TIMESPAN = pd.Timedelta(days=14)

parser = argparse.ArgumentParser(description="Plot standby availability over time")
parser.add_argument("--origin", required=True, help="airport code of the flight origin")
parser.add_argument("--destination", required=True, help="airport code of the flight destinatation")
parser.add_argument("--start_datetime", required=False, default=pd.Timestamp.now() - DEFAULT_TIMESPAN, help="starting datetime for the span of time to search for flight availability data")
parser.add_argument("--end_datetime", required=False, default=pd.Timestamp.now(), help="ending datetime for the span of time to search for flight availability data")


args = parser.parse_args()
origin = args.origin
destination = args.destination
start_datetime = args.start_datetime
end_datetime = args.end_datetime

db_connection = psycopg2.connect(
  dbname="standby_data",
  user="postgres",
  password="9476",
  host="localhost",
  port=5432
)

query = """
SELECT
  FLOOR(EXTRACT(EPOCH FROM (f.scheduled_departure_datetime - r.record_datetime)) / 3600) AS hours_before_departure,
  AVG(r.seats_available) AS avg_available_seats
FROM readings r
JOIN flights f ON r.flight_id = f.id
JOIN airports origin ON f.origin_airport_id = origin.id
JOIN airports destination ON f.destination_airport_id = destination.id
WHERE origin.code = %s
  AND destination.code = %s
  AND f.scheduled_departure_datetime BETWEEN %s AND %s
GROUP BY hours_before_departure
ORDER BY hours_before_departure DESC;
"""

data = pd.read_sql(query, db_connection, params=(origin, destination, start_datetime, end_datetime))
db_connection.close()

print(data)

plt.figure(figsize=(10, 5))
plt.plot(data["hours_before_departure"], data["avg_available_seats"], marker='o')
# plt.gca().invert_xaxis()
plt.ylim(0, 20)
plt.xlim(0, 168)
plt.title(f"Average Seat Availability From {origin} to {destination}")
plt.xlabel("Hours Before Departure")
plt.ylabel("Average Available Seats")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"data/average_availability_{origin}_{destination}_{start_datetime}_{end_datetime}.png")
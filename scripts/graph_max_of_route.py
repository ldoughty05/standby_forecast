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
parser.add_argument("--bucket_mode", required=False, choices=["hourly", "fib"], default="hourly", help="Mode in which to bucket sample data. By the hour or fibonacci sequence.")



args = parser.parse_args()
origin = args.origin
destination = args.destination
start_datetime = args.start_datetime
end_datetime = args.end_datetime
bucket_mode = args.bucket_mode

db_connection = psycopg2.connect(
  dbname="standby_data",
  user="postgres",
  password="9476",
  host="localhost",
  port=5432
)

query_hourly = """
SELECT
  FLOOR(EXTRACT(EPOCH FROM (f.scheduled_departure_datetime - r.record_datetime)) / 3600) AS hours_before_departure,
  MAX(r.seats_available) AS max_available_seats
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

query_fib = """
WITH with_hours AS (
  SELECT
    r.seats_available,
    FLOOR(EXTRACT(EPOCH FROM (f.scheduled_departure_datetime - r.record_datetime)) / 3600) AS hours_before_departure
  FROM readings r
  JOIN flights f ON r.flight_id = f.id
  JOIN airports origin ON f.origin_airport_id = origin.id
  JOIN airports destination ON f.destination_airport_id = destination.id
  WHERE origin.code = %s
    AND destination.code = %s
    AND f.scheduled_departure_datetime BETWEEN %s AND %s
)

SELECT
  CASE
    WHEN hours_before_departure < 1 THEN 0
    WHEN hours_before_departure < 2 THEN 1
    WHEN hours_before_departure < 3 THEN 2
    WHEN hours_before_departure < 5 THEN 3
    WHEN hours_before_departure < 8 THEN 5
    WHEN hours_before_departure < 13 THEN 8
    WHEN hours_before_departure < 21 THEN 13
    WHEN hours_before_departure < 34 THEN 21
    WHEN hours_before_departure < 55 THEN 34
    WHEN hours_before_departure < 89 THEN 55
    WHEN hours_before_departure < 144 THEN 89
    WHEN hours_before_departure < 168 THEN 144
    ELSE 168
  END AS fibonacci_bucket,
  MAX(seats_available) AS max_available_seats
FROM with_hours
GROUP BY fibonacci_bucket
ORDER BY fibonacci_bucket DESC;
"""

if bucket_mode == "fib":
  query = query_fib
  print("bucket_mode: fib")
else:
  print("bucket_mode: hourly")
  query = query_hourly

data = pd.read_sql(query, db_connection, params=(origin, destination, start_datetime, end_datetime))
db_connection.close()

plt.figure(figsize=(10, 5))

if bucket_mode == "fib":
  plt.plot(data["fibonacci_bucket"], data["max_available_seats"], marker='o')
else:
  plt.plot(data["hours_before_departure"], data["max_available_seats"], marker='o')

# plt.gca().invert_xaxis()
plt.ylim(-5, 20)
plt.xlim(0, 168)
plt.title(f"Best Case Seat Availability From {origin} to {destination}")
plt.xlabel("Hours Before Departure")
plt.ylabel("Maximum Available Seats")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"data/max_availability_{origin}_{destination}_{bucket_mode}_{start_datetime}_{end_datetime}.png")
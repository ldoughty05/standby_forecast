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
parser.add_argument("--start_datetime", required=False, default=pd.Timestamp.now() - DEFAULT_TIMESPAN, help="starting datetime for the span of time to search for flight availability data")
parser.add_argument("--end_datetime", required=False, default=pd.Timestamp.now(), help="ending datetime for the span of time to search for flight availability data")
parser.add_argument("--bucket_mode", required=False, choices=["hourly", "fib"], default="hourly", help="Mode in which to bucket sample data. By the hour or fibonacci sequence.")


args = parser.parse_args()
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
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.seats_available) AS median_available_seats
FROM readings r
JOIN flights f ON r.flight_id = f.id
WHERE f.scheduled_departure_datetime BETWEEN %s AND %s
  AND r.total_capacity = 50
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
  WHERE f.scheduled_departure_datetime BETWEEN %s AND %s
    AND r.total_capacity = 50
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
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY seats_available) AS median_available_seats
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

data = pd.read_sql(query, db_connection, params=(start_datetime, end_datetime))
db_connection.close()

plt.figure(figsize=(10, 5))

if bucket_mode == "fib":
  plt.plot(data["fibonacci_bucket"], data["median_available_seats"], marker='o')
else:
  plt.plot(data["hours_before_departure"], data["median_available_seats"], marker='o')

# plt.gca().invert_xaxis()
plt.xlim(0, 168)
plt.title(f"Median Seat Availability of flights with a capacity of 50")
plt.xlabel("Hours Before Departure")
plt.ylabel("Median Available Seats")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"data/median_availability_AllFlights_50Capacity_{bucket_mode}_{start_datetime}_{end_datetime}.png")
---------------------------------------------------------------------------------------------
-- CREATING TABLES
---------------------------------------------------------------------------------------------

-- CREATE TABLE airports (
--     id SERIAL PRIMARY KEY,
--     name TEXT NOT NULL,
--     code VARCHAR(10) UNIQUE NOT NULL
-- );

-- CREATE TABLE flights (
--     id SERIAL PRIMARY KEY,
--     -- flight_number TEXT NOT NULL,
--     origin_airport_id INT REFERENCES airports(id),
--     destination_airport_id INT REFERENCES airports(id),
--     scheduled_departure_datetime TIMESTAMP NOT NULL
-- );

-- CREATE TABLE readings (
--     id SERIAL PRIMARY KEY,
--     flight_id INT REFERENCES flights(id),
--     record_datetime TIMESTAMP NOT NULL,
--     seats_available INT,
--     standby_count INT,
--     total_capacity INT
-- );


-- CREATE TABLE passrider_data_staging (
--   departure_datetime TIMESTAMP,
--   record_datetime TIMESTAMP,
--   origin TEXT,
--   destination TEXT,
--   available_seats INT,
--   standby_count INT,
--   total_capacity INT
-- );

---------------------------------------------------------------------------------------------
-- POPULATE TABLES WITH DATA FROM STAGING
---------------------------------------------------------------------------------------------
INSERT INTO airports (code)
SELECT DISTINCT origin FROM passrider_data_staging
ON CONFLICT (code) DO NOTHING;

INSERT INTO airports (code)
SELECT DISTINCT destination FROM passrider_data_staging
ON CONFLICT (code) DO NOTHING;

-- Creates a new rule preventing duplicate flights 
CREATE UNIQUE INDEX unique_flight ON flights(origin_airport_id, destination_airport_id, scheduled_departure_datetime);

INSERT INTO flights (origin_airport_id, destination_airport_id, scheduled_departure_datetime)
SELECT
  oa.id,
  da.id,
  staging.departure_datetime
FROM passrider_data_staging staging
JOIN airports oa ON oa.code = staging.origin
JOIN airports da ON da.code = staging.destination
ON CONFLICT DO NOTHING;
  
INSERT INTO readings (flight_id, record_datetime, seats_available, standby_count, total_capacity)
SELECT
  f.id,
  staging.record_datetime,
  staging.available_seats,
  staging.standby_count,
  staging.total_capacity
FROM passrider_data_staging staging
JOIN airports oa ON oa.code = staging.origin
JOIN airports da ON da.code = staging.destination
JOIN flights f 
  ON f.origin_airport_id = oa.id
  AND f.destination_airport_id = da.id
  AND f.scheduled_departure_datetime = staging.departure_datetime;

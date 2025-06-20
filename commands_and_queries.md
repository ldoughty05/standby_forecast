# get flights on a certain day
```{sql}
SELECT f.id, f.scheduled_departure_datetime
FROM flights f
JOIN airports ao ON f.origin_airport_id = ao.id
JOIN airports ad ON f.destination_airport_id = ad.id
WHERE ao.code = 'ORD'
  AND ad.code = 'AVP'
  AND DATE(f.scheduled_departure_datetime) = '2025-06-19'
ORDER BY f.scheduled_departure_datetime;
```

# get most recent flights
```{sql}
standby_data=# SELECT f.id, f.scheduled_departure_datetime
FROM flights f
JOIN airports ao ON f.origin_airport_id = ao.id
JOIN airports ad ON f.destination_airport_id = ad.id
WHERE ao.code = 'ORD'
  AND ad.code = 'AVP'
ORDER BY f.scheduled_departure_datetime DESC
LIMIT 5;
```
# run database initializer script
done locally (WSL not docker) but -h sends it to the postgres server
```{bash}
psql -h localhost -U postgres -d standby_data -f init_standby_data_db.sql
```

# send file to tmp
so I can run the sql script from local
```{bash}
cp init_standby_data_db.sql /tmp/
```

# open postgres CLI (in docker container)
this worked once but not the second time
```{bash}
psql -h localhost -U postgres -d standby_data
```

# turn on docker container
while in .devcontainer directory
```{bash}
docker compose up -d
```

# enter docker shell then open postgres CLI
```{bash}
docker exec -it pg-standby bash
psql -U postgres -d standby_data
```

# upload csv data to staging area
done locally but sent to the postgres server in the docker container
```{sql}
\copy passrider_data_staging FROM '/full/path/to/cleaned_flight_data.csv' DELIMITER ',' CSV HEADER;
```


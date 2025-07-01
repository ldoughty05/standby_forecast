# Standby Seat Availability Forecaster
by Luke Doughty

## This repository contains:
*  a short dataset of seat availability during the month of June 2025
*  script to get flight information including seat availability from a publicly available United Airlines API
*  multiple scripts to generate graphs based on the collected data
*  scripts to initialize a postgreSQL database and a script to upload csv data to it

## Creating the database:
I ran all of the code in this repository in a WSL2 Ubuntu window. Because of WSL weirdness, scalability, and because I wanted to learn, the postgreSQL database is run inside of a docker container. This made it easy to boot up the container and not have to worry about dependencies, while also making it easy to access via TCP.

To create the PostgreSQL database, first create a docker container with a docker-compose.yml that looks something like the following:  
```{yml}
services:
  postgres:
    image: postgres:14
    container_name: pg-standby
    restart: always
    environment:
      POSTGRES_DB: standby_data
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: XXXX
    ports:
      - "5432:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data
```
You can start up the docker container using  
```{bash}
cd .devcontainer
docker compose up -d
```
To create the database tables, run the "CREATING TABLES" half of `init_standby_data_db.sql` by doing the following:  
```{bash}
cp init_standby_data_db.sql /tmp/
psql -h localhost -U postgres -d standby_data -f init_standby_data_db.sql
```

Commands for entering the container shell are in `commands_and_queries.md`.  
To populate the database, run the following in your WSL shell (not the container):
```{sql}
\copy passrider_data_staging FROM 'data/cleaned_standby_data.csv' DELIMITER ',' CSV HEADER;
```

The last step simply brought the csv data into the staging table. To send that data into the actual tables, run the "POPULATE TABLES WITH DATA FROM STAGING" half of `init_standby_data_db.sql`:
```{bash}
cp init_standby_data_db.sql /tmp/
psql -h localhost -U postgres -d standby_data -f init_standby_data_db.sql
```

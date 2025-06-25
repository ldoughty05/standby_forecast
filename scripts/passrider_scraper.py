#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from datetime import datetime, timedelta
import csv


# In[2]:


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

def load_secrets(filepath="secrets.txt"):
  secrets = {}
  with open(filepath, 'r') as file:
    for line in file:
      if '=' in line:
        key, value = line.strip().split('=', 1)
        secrets[key] = value
  return secrets
secrets = load_secrets()
USERNAME = secrets['username']
PASSWORD = secrets['password']
CLIENT_ID = secrets['client_id']
TRANSACTION_ID = secrets['transaction_id']
X_DTPC = secrets['x_dtpc']


# ## Login to get token

# In[3]:


session = requests.Session() # Automatically handles cookies

login_payload = {
  "client_id":CLIENT_ID,
  "username":USERNAME,
  "password":PASSWORD,
  "scope":"empres",
  "grant_type":"password"
}

login_headers = {
  "Sec-Ch-Ua-Platform": "Windows",
  "Accept-Language": "en-US,en;q=0.9",
  "X-Dtpc": "-69$513377965_229h12vENMACHVVLMVHCCWOILMFBUIRAHDQNPQR-0e0",
  "Sec-Ch-Ua": '"Not.A/Brand";v="99", "Chromium";v="136"',
  "Sec-Ch-Ua-Mobile": "?0",
  "Access-Control-Allow-Origin": "*",
  "User-Agent": USER_AGENT,
  "Accept": "application/json, text/plain, */*",
  "Content-Type": "application/json",
  "Origin": "https://erespassriderndc.united.com",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Dest": "empty",
  "Referer": "https://erespassriderndc.united.com/passriderlogin/",
  "Accept-Encoding": "gzip, deflate, br"
}

token_request_url = "https://erespassriderndc.united.com/token"

token_response = session.post(
  token_request_url,
  json=login_payload,
  headers=login_headers
)

token = token_response.json().get("access_token")

# ## Get Nonrev Flights

# In[5]:


def searchFlights(departure_date, origin, destination):
  flight_search_url = "https://erespassriderndc.united.com/EmployeeResAPI/api/FlightSearch/FlightSearchResult"
  flight_search_headers = {
    "Sec-Ch-Ua-Platform": "Windows",
    "Authorization": f"Bearer {token}",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Dtpc": X_DTPC,
    "Sec-Ch-Ua": '"Not.A/Brand";v="99", "Chromium";v="136"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
    "Access-Control-Allow-Origin": "*",
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Headers": "Authorization",
    "Origin": "https://erespassriderndc.united.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://erespassriderndc.united.com/EmployeeRes/fsrsearch",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i",
  }
  flight_search_payload = {
    "Trips":[
      {
        "Origin":origin,
        "Destination":destination,
        "DepartDate":departure_date,
        "DependantID":["5901271"],
        "TripId":0
      }
    ],
    "ReturnDate":None,
    "MaxConnections":"ANY",
    "MaxNumberOfTrips":"5",
    "TravelTypeCode":"P",
    "QualifiedEmergency":None,
    "EmergencyNature":None,
    "SearchType":"OW",
    "TransactionId":TRANSACTION_ID,
    "IsPassRiderLoggedIn":True,
    "IncludeSSRUMNR":False
  }
  flight_search_response = session.post(flight_search_url, json=flight_search_payload, headers=flight_search_headers)
  print(flight_search_response.status_code)
  return flight_search_response.json()


# In[6]:


NUM_DAYS_CHECKED = 7  # number of days after departure date to check for flights.


# In[ ]:


routes = []
with open('routes.csv', 'r', newline='') as csvfile:
  reader = csv.reader(csvfile)
  for row in reader:
    if len(row) == 2:
      origin, destination = row
      routes.append((origin, destination))
      routes.append((destination, origin))


# In[8]:


date = datetime.now()
search_flights_results = []
for route in routes:
  origin, destination = route
  for day_offset in range(NUM_DAYS_CHECKED):
    flight_date = (date + timedelta(days=day_offset)).strftime("%m/%d/%Y")
    try:
      daily_results = searchFlights(flight_date, origin, destination)["AvailableRoutes"]["Routes"]
      search_flights_results.extend(daily_results)
    except (TypeError, KeyError) as e:
      continue

# Getting a "remote disconnected" usually means you need a new token.
# Getting NoneType errors means to use burp to get a new transaction_id, and maybe a new X-Dtpc value.


# ## Save data to csv
# departure_date, departure_time, record_date, record_time, origin, destination, available, standby

# In[9]:

csv_rows = []
for flight in search_flights_results:
  if len(flight["Segments"]) > 1:
    continue  # Skip flights with connections
  flight_info = flight["Segments"][0]
  origin = flight_info["Origin"]["AirportCode"]
  destination = flight_info["Destination"]["AirportCode"]
  departure_date = flight_info["DepartureDate"]
  departure_time = flight_info["DepartureTime"]
  available = flight_info["Available"]["Total"]
  standby = flight_info["SA"]["Total"]
  capacity = flight_info["Capacity"]["Total"]

  record_datetime = datetime.now()
  csv_rows.append([
    departure_date,
    departure_time,
    record_datetime.strftime("%m/%d/%Y"),
    record_datetime.strftime("%H:%M"),
    origin,
    destination,
    available,
    standby,
    capacity
  ])


with open('data/standby_data.csv', 'a', newline='') as csvfile:
  writer = csv.writer(csvfile)
  for row in csv_rows:
    writer.writerow(row)
  


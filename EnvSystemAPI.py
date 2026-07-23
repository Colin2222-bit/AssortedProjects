#PROJECT 2 - AOSC Senior Research: Pulling data from API endpoints of Maryland and national environmental networks. Data availability is important for the overall economic value proposition of integrated network system in project


#MONITORING SYSTEM 1: Chesapeake Eyes on the Bay Program

import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import dataretrieval.waterdata as waterdata

baseurl = 'https://mw.buoybay.noaa.gov/api/v1'
# API = *your API key*

# 1. One specific station 
station = 'AN'
endpoint = f"{baseurl}/json/query/{station}"

# 2. Put query variables into the params dictionary 
params = {
    'key': API,
    'sd': '2026-06-29T10:00:00z',
    'ed': '2026-06-30T20:00:00z',
    'var': 'all' # Consider changing 'all' to specific vars like 'air_temperature' if needed
}

def endpointtoplot(endpoint, parameters):
    print(f"Requesting data from {endpoint}...")

    try:
        # 3. Add a timeout 
        response = requests.get(endpoint, params=parameters, timeout=30)
        response.raise_for_status() # This will raise an error for bad HTTP codes (404, 500, etc.)
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return

    data = response.json()

    for buoy in data.get('stations', []):
        print(f"STATION: {buoy['stationLongName']}")

        for var in buoy.get('variable', []):
            print(var['reportName'])

            # Grabbing the latest 10 measurements and reversing them for chronological order
            measurements = var.get('measurements', [])
            if not measurements:
                continue

            latest = measurements[:10][::-1]

            plt.figure(figsize=(10, 6))
            plt.ylabel(f"{var['reportName']} - {var.get('units', '')}")

            if var.get('elevation', 0) != 0 and var.get('elevation', '0.0') != '0.0':
                plt.title(f"{var['reportName']} - {buoy['stationLongName']} : Elevation: {var['elevation']} m")
            else:
                plt.title(f"{var['reportName']} - {buoy['stationLongName']}")

            tenval = pd.DataFrame(latest)
            print(tenval)

            tenval['time'] = pd.to_datetime(tenval['time'])
            tenval = tenval.sort_values('time')
            tenval['value'] = pd.to_numeric(tenval['value'])

            plt.plot(tenval['time'], tenval['value'], marker='o', color='green', linestyle='-')

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.tight_layout()

            # Save and show
            safe_name = f"{var['reportName'].replace('/', '_')} - {buoy['stationLongName']}.png"
            plt.savefig(safe_name)
            plt.show()

endpointtoplot(endpoint, params)


#MONITORING SYSTEM 2: Chesapeake Eyes on the Bay Program

def check_chesapeake_status():
    base_url = "https://datahub.chesapeakebay.net/api/WaterQuality"
    headers = {'Accept': 'application/json'}

    # 1. Isolating just the 2020 and 2026 date ranges for testing
    date_ranges = [
        ("06-29-2020", "12-31-2020"),
        ("01-01-2025", "03-01-2025")
    ]

    stream = "0,1"
    progs = "2,4,6"
    projs = "2,7,12,13,14"
    geo_attr = "HUC8"
    attr_id = "1,2,3,4,5,6,8,10,12,17,22,24,27,29,31,33,35"
    substance_id = "12,21,30,46,73,117,120,123,128,130"

    substances_dict = {
        "BOD5W": "5-Day Biochemical Oxygen Demand",
        "CHLA": "Active Chlorophyll",
        "DIN": "Dissolved Inorganic Nitrogen",
        "FLOW_INS": "Stream Flow; Instantaneous",
        "WTEMP": "Water Temperature",
        "PRESSURE": "Barometric Pressure",
        "TURB_FNU": "Turbidity",
        "PH": "pH levels"
    }

    all_data = []

    # 2. Diagnostic loop
    for start, end in date_ranges:
        api_url = f"{base_url}/{start}/{end}/{stream}/{progs}/{projs}/{geo_attr}/{attr_id}/{substance_id}"

        print(f"--- Testing Dates: {start} to {end} ---")

        try:
            response = requests.get(api_url, headers=headers, timeout=60)

            # Print the exact HTTP status code so you know exactly how the server responded
            print(f"Status Code: {response.status_code}")

            response.raise_for_status()

            data = response.json()
            if data:
                print(f"Success: Retrieved {len(data)} records for this period.\n")
                all_data.extend(data)
            else:
                print("Warning: Request succeeded, but 0 records were returned (Empty JSON).\n")

            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"FAILED: The request was rejected or timed out.")
            print(f"Error Details: {e}\n")

    # 3. Only proceed to plotting if we actually got data back
    if not all_data:
        print("No data retrieved from either request. Exiting script.")
        return

    print(f"Successfully compiled {len(all_data)} total records. Generating plots...")

    df = pd.DataFrame(all_data)

    print(df.columns)


    # Updated to 'sampleDate' and 'measureValue'
    df['SampleDate'] = pd.to_datetime(df['SampleDate'])
    df['measureValue'] = pd.to_numeric(df['measureValue'], errors='coerce')
    df = df.sort_values(['SampleDate'])

    # Updated to 'parameter'
    for param, group in df.groupby('parameter'):
        plt.figure(figsize=(15, 6))

        # Updated to 'station'
        for station_name, group2 in group.groupby('station'):
            plt.plot(group2['SampleDate'], group2['measureValue'], label=station_name, marker='o', linestyle='-')

        param_code = group['parameter'].iloc[0]
        substance_name = substances_dict.get(param_code, param_code)

        # Updated to 'measureUnit'
        unit = group['measureUnit'].iloc[0] if 'measureUnit' in group.columns else ''

        # Convert substance_name to string just in case, to prevent .replace() errors
        safe_substance_name = str(substance_name).replace('/', ' per ')

        plt.ylabel(f"{substance_name} - {unit}")
        plt.title(f"{safe_substance_name} - Diagnostic Run")
        plt.xlabel("Date")

        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %Y'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        plt.savefig(f"{safe_substance_name}_diagnostic.png")
        plt.show()




# Run the function
check_chesapeake_status()



#MONITORING SYSTEM 3: MDE Ambient Air Quality Monitoring Network

#api_key = “your MDE API key”
zip_code = "20740"
base_url = "https://www.airnowapi.org/aq/KML/PM25/"

params = {
    "date": "2022-01-01T13",

    "bbox": "-118,34,-71,42",
    "srs": "EPSG:4326",
    "api_key": api_key
        }

response = requests.get(base_url, params=params)
kml_content = response.text


with open("air_quality2.kml", "w") as f:
    f.write(kml_content)
    print('air_quality.kml')




print(f"--- Current Air Quality for {zip_code} ({data[0]['ReportingArea']}, {data[0]['StateCode']}) ---")
for entry in data:
            print(f"Pollutant: {entry['ParameterName']}")
            print(f"AQI: {entry['AQI']}")
            print(f"Location: {entry['Latitude']} {entry['Longitude']}")
            print(f"Category: {entry['Category']}")
            print(f"Time:      {entry['DateObserved']} {entry['HourObserved']}:00 {entry['LocalTimeZone']}")
            print("-" * 40)

#Future air quality forecasts
zip_codes = ["20740","21042","20001"]
base_url = "https://www.airnowapi.org/aq/forecast/zipCode/"


for zip_code in zip_codes:
  params = {
      "zipCode": zip_code,

      'distance' : 10000,
      'format' : 'application/json',
      "api_key": api_key
          }

  response = requests.get(base_url, params=params)
  data=response.json()
  df=pd.DataFrame(data)
  print(df.columns)


# DateTime conversion
  df['DateForecast'] = pd.to_datetime(df['DateForecast'])

  plt.figure(figsize=(10, 6))

  # Use seaborn to color the dots based on the ParameterName (e.g., OZONE vs PM2.5)
  sns.scatterplot(
      data=df,
      x='DateForecast',
      y='AQI',
      hue='ParameterName',
      style='ReportingArea',
      s=100
  )

  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
  plt.gca().xaxis.set_major_locator(mdates.DayLocator())

  plt.title(f"AQI Forecast: {zip_code}")
  plt.xlabel('Date')
  plt.ylabel('AQI')
  plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
  plt.tight_layout()
  plt.show()



#MONITORING SYSTEM 4: USGS water/atream quality data

base_url = 'https://api.waterdata.usgs.gov/ogcapi/v0'
endpoint = f"{base_url}/collections/latest-continuous/items"

params = {

    "limit": 100,
    "bbox": "-77.5,38.5,-76.0,39.5",
    "parameter_code": '00010'

}
response = requests.get(endpoint, params=params)
data = response.json()
df=pd.json_normalize(data['features'])
df=df.sort_values('properties.time')
df['properties.time'] = pd.to_datetime(df['properties.time'])
df = df[['properties.monitoring_location_id',
         'properties.time',
         'properties.value']].rename(columns={
    'properties.monitoring_location_id': 'Station',
    'properties.time': 'Time',
    'properties.value': 'Water Temperature (Celcius)'
})

print(df)







#Available keys in properties: ['id', 'time_series_id', 'monitoring_location_id', 'parameter_code', 'statistic_id', 'time', 'value', 'unit_of_measure', 'approval_status', 'qualifier', 'last_modified']




# 1. Define lists 
siteIDs = ['USGS-10109000', 'USGS-01649500', 'USGS-01650800', 'USGS-01651003', 'USGS-01651730']
parameterCodes = ["00060", "00065", "00010"]
time_window = "PT24H"


data_tuple = waterdata.get_continuous(
    monitoring_location_id=siteIDs,
    parameter_code=parameterCodes,
    time=time_window
)

df = data_tuple[0]


if not df.empty:
    print(f"Successfully retrieved {len(df)} records for all sites/params.")

  
    summary = df.groupby(['monitoring_location_id', 'parameter_code']).size()
    print("\nData availability summary:")
    print(summary)

else:
    print("No data found.")


param_map = {
    "00060": "Discharge (ft³/s)",
    "00065": "Gage Height (ft)",
    "00010": "Water Temperature (°C)"
}

# 2. Datetime
df['time'] = pd.to_datetime(df['time'])
df['value'] = pd.to_numeric(df['value'])

# 3. Create a separate plot for each parameter
for param_code, group_df in df.groupby('parameter_code'):
    plt.figure(figsize=(12, 6))

    # Use seaborn to automatically color-code the different sites
    sns.lineplot(
        data=group_df,
        x='time',
        y='value',
        hue='monitoring_location_id',
        marker='o',
        markersize=4
    )

    plt.title(f"Operational Trend: {param_map.get(param_code, param_code)}")
    plt.ylabel(param_map.get(param_code, param_code))
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

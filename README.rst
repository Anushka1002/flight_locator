# FlightLocator

FlightLocator is a small Python library for calculating details the following details during a flight: coordinates where sunset/sunrise happened during the flight, the date and time of sunrise/sunset, the total duration of the flight, night duration of the flight, average speed of the flight when the flight started and ended i.e gives you day/night and list of all the latitude-longitude after every 10km from start to end.

Firstly the distance between start and end coordinates of the flight is calculated using haversine formula then coordinates after every 10km are calculated using destination point formula. After that DateTime and sunset/sunset during the entire journey are calculated and the final result is computed.

All the formulas used like Harvesine formula for calculating distance, bearing formula, calculating destination point formula are taken from https://www.movable-type.co.uk/scripts/latlong.html. Sunrise and sunset points calculations are inspired by getPositon method in the SunCalc library by Vladimir Agafonkin @mourner.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

flight_enroute_postion = flight_locator.get_flight_route_data(1.3644, 103.9915,
                                                              "20200414T08:00:00Z",
                                                              33.9416, -118.4085,
                                                              "20200414T21:00:00Z")


Expected Response
{
        "start": "night",
        "end": "day",
        "travel_distance": 9902.773515349885,
        "total_duration": "10:45:00",
        "speed": 497.40185420412297,
        "point_sunset_info": [],
        "point_sunrise_info": [
            {
                "enroute_sunrise_lat": 41.68808885038308,
                "enroute_sunrise_long": 61.3187183378937,
                "datetime_of_sunrise": "2019-02-08T03:06:46.661631Z",
                "sunrise_on_route": true,
                "sunset_on_route": false
            }
        ],
        "night_duration": "05:07:00",
        "enroute_coordinates": [
        { lat: 28.556105, long: 77.0998612 },
        { lat: 28.473404652040816, long: 77.05964998607098 },
        { lat: 28.390692495681854, long: 77.01950168462119 },
        { lat: 28.30796858994826, long: 76.97941599009319 },
        { lat: 28.225232993591774, long: 76.9393925982526 },
        { lat: 28.14248576509259, long: 76.89943120617976 },
        ............ more]
    }
```


## Function Detail
```python

def get_flight_route_data(start_lat, start_long, start_datetime,
                          end_lat, end_long, end_datetime)


:params start_lat : source's latitude
:params start_long : source's longitude
:params start_datetime : flight's departure time
:params end_lat : destination's latitude
:params end_long : destination's latitude
:params end_datetime : flight's arrival latitude

```
## Response Details

| Property           | Description                                                               |
| -------------------| --------------------------------------------------------------------------|
| `start`            | flight Departure occurred during day/night                          |
| `end`              | flight Arrival occurred during day/night                                |
| `travel_distance`  | distance between flight source and destination (in kms)                   |
| `total_duration`   | total duration of flight in HH:MM:SS                                      |
| `night_duration`   | total night hours during the flight in HH:MM:SS                           |
| `sunrisePointInfo` | contains enroute_sunrise_lat, enroute_sunrise_long,datetime_of_sunrise   |
| `sunsetPointInfo`  | contains  enroute_sunset_lat, enroute_sunset_long, datetime_of_sunset     |
| `speed`            | average speed of entire journey in nautical mile per hour                 |
| `points_enroute`   | list of (latitutde , longitude) at every 10km from start till end


|------------------------------------------------------------------------------------------------|
| ## `sunsetPointInfo` is an object with following properties:                                   |
|------------------------------------------------------------------------------------------------|
| `enroute_sunset_lat`  | latitude at which sunset occurred                                       |
| `enroute_sunset_long` | longitude at which sunset occurred                                      |
| `datetime_of_sunset`  | date and time at which sunset occurred in UTC(YYYY-MM-DDT00:00:00.000Z) |
|------------------------------------------------------------------------------------------------|


|------------------------------------------------------------------------------------------------|
|`sunrisePointInfo` is an object with the following properties:                                  |
|------------------------------------------------------------------------------------------------|
| `enroute_sunrise_lat` | latitude at which sunrise occurred                                      |
| `enroute_sunrise_long`| longitude at which sunrise occurred                                     |
| `datetime_of_sunrise` | date and time at which sunrise occurred in UTC(YYYY-MM-DDT00:00:00.000Z)|

|------------------------------------------------------------------------------------------------|

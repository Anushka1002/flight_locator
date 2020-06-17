
## Prerequisite:

    * Python 3.x
    * Django 3.x

## FlightLocator


    FlightLocator is a small Python library for calculating details the following details during a flight : coordinates where sunset/sunrise happened during the flight, the date and time of sunrise/sunset, total duration of flight, night duration of flight, average aoeed of the flight, when the flight started and ended i.e gives you â€˜day/nightâ€™ and list of all the latitude longitude after every 10km from start to end.

    Firstly the distance between start and end coordinates of the flight is calculated using haversine formula then coordinates after every 10km are calculated using destination point formula. After that datetime and sunset/sunset during the entire journey is calculated and final result is computed.

    All the formulas used like Harvesine formula for calculating distance, bearing formula, calculating destination point formula aretaken from https://www.movable-type.co.uk/scripts/latlong.html. Sunrise and sunset points calculations are inspired by getPositon method in the SunCalc library by Vladimir Agafonkin @mourner.

### Usage example

```python
    * Sample Request
    {
        "start_lat": 51.4700,
        "start_long": -0.4543,
        "start_datetime": "20190207T22:00:00Z",
        "end_lat": 8.1111,
        "end_long": 98.3065,
        "end_datetime": "20190208T08:45:00Z"
    }

    response = flight_locator.get_flight_route_data(51.4700, -0.4543, "20190207T22:00:00Z", 8.1111, 98.3065, "20190208T08:45:00Z")

    * Expected Response:
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

FlightLocator can be downloaded and copied in Pythom project as well.
import flightLocator from '../flightLocator';
use => flightLocator.getFlightDetails(this.sampleJSON);

For JS:
var flightLocator = require('flightLocator');

## Reference

### Flight Details

``python
flightLocator.getFlightDetails(
    {/*float*/ start_lat,
     /*float*/ start_long,
     /*String (UTC time 'YYYYMMDDT00:00:00Z')*/ start_datetime,
     /*float*/ end_lat
     /*float*/ end_long
     /*String (UTC time 'YYYYMMDDT00:00:00Z')*/ end_datetime,
     }
     )
```

Returns JSON object with the following properties
|------------------------------------------------------------------------------------------------|
| Property           | Description                                                               |
| -------------------| --------------------------------------------------------------------------|
| `start`            | flight Departure occurred during â€˜day/nightâ€™                              |
| `end`              | flight Arrival occurred during â€˜day/nightâ€™                                |
| `travel_distance`  | distance between flight source and destination (in kms)                   |
| `total_duration`   | total duration of flight in HH:MM:SS                                      |
| `night_duration`   | total night hours during the flight in HH:MM:SS                           |
| `sunrisePointInfo` | contains enroute_sunrise_lat, enroute_sunrise_long, datetime_of_sunrise   |
| `sunsetPointInfo`  | contains  enroute_sunset_lat, enroute_sunset_long, datetime_of_sunset     |
| `speed`            | average speed of entire journey in nautical mile per hour                 |
| `points_enroute`   | array of (latitutde , longitude) at every 10km from start till end        |
|------------------------------------------------------------------------------------------------|


|------------------------------------------------------------------------------------------------|
| ## `sunsetPointInfo` is an object with following properties:                                   |
|------------------------------------------------------------------------------------------------|
| `enroute_sunset_lat`  | latitude at which sunset occured                                       |
| `enroute_sunset_long` | longitude at which sunset occured                                      |
| `datetime_of_sunset`  | date and time at which sunset occured in UTC(YYYY-MM-DDT00:00:00.000Z) |
|------------------------------------------------------------------------------------------------|


|------------------------------------------------------------------------------------------------|
| ## `sunrisePointInfo` is an object with following properties:                                  |
|------------------------------------------------------------------------------------------------|
| `enroute_sunrise_lat` | latitude at which sunrise occured                                      |
| `enroute_sunrise_long`| longitude at which sunrise occured                                     |
| `datetime_of_sunrise` | date and time at which sunrise occured in UTC(YYYY-MM-DDT00:00:00.000Z)|
|------------------------------------------------------------------------------------------------|




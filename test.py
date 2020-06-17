from python_package.flight_locator import get_flight_route_data


test_data = {
    "start_lat": 51.4700,
    "start_long": -0.4543,
    "start_datetime": "20190207T22:00:00Z",
    "end_lat": 8.1111,
    "end_long": 98.3065,
    "end_datetime": "20190208T08:45:00Z"
}

expected_response = {
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
                                "sunrise_on_route": True,
                                "sunset_on_route": False
                            }
                        ],
                        "night_duration": "05:07:00"
}
# we have not added enroute coordinates in expected response above.

result = get_flight_route_data(test_data["start_lat"], test_data["start_long"], test_data["start_datetime"],
                               test_data["end_datetime"], test_data["end_lat"], test_data["end_long"])

print(result)

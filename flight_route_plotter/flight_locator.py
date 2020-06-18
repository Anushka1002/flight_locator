"""
    flight_route_plotter controller file
"""
import math
import time
from datetime import datetime, timedelta

import pytz
from . suncalc_v2 import getPosition
from geographiclib.geodesic import Geodesic
from geopy.distance import lonlat, great_circle


def get_bearing(start_point, end_point):
    """
    * Method to calculate bearing between two coordinates.

    ***
        :param: start_point: start coordinate```
        :param: end_point: end coordinate

    * return float: bearing betweem two coordinates"""

    # φ1 = this.degreesToRadians(lat1)
    lat1 = math.radians(start_point[0])

    # φ2 = this.degreesToRadians(lat2)
    lat2 = math.radians(end_point[0])

    # λ1 = this.degreesToRadians(lng1)
    lon1 = math.radians(start_point[1])

    # λ2 = this.degreesToRadians(lng2)
    lon2 = math.radians(end_point[1])

    # y = Math.sin(λ2 - λ1) * Math.cos(φ2)
    y = math.sin(lon2-lon1) * math.cos(lat2)

    # x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(λ2 - λ1);
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2-lon1)
    theta = math.atan2(y, x)
    bearing = (theta * 180 / math.pi + 360) % 360
    return bearing


def get_positional_data(A, B, speed, start_datetime_obj):
    """
    * Method to get sun positional data

    ***
        :params A: start coordinate
        :params B: end coordinate
        :params speed: speed of flight
        :params start_datetime_obj: start_datetime_obj
    * return:
    ***
        C : next coordinate
        sun_position : sun's positio on next coordinate
        time_at_c : time at C
    """
    geod = Geodesic.WGS84
    # azimuth between start and end points
    inv = geod.Inverse(A[0], A[1], B[0], B[1])

    bearing = get_bearing(A, B)

    s_in_km = 10
    s_in_meter = 10 * 1000

    # geocodes of 10km distant point
    dir = geod.Direct(A[0], A[1], bearing, s_in_meter)
    C = (dir['lat2'], dir['lon2'])

    c_reaching_time = s_in_km / speed

    # Time when flight reaches C
    time_at_c = start_datetime_obj.astimezone(pytz.timezone("UTC")) + timedelta(hours=c_reaching_time)

    # sun's position at C
    sun_position = getPosition(time_at_c, A[0], A[1])

    return sun_position, time_at_c, C


def get_roundoff_time(total_seconds):
    """
    * Method to round off time into nearest minutes
    ***
        :params total_seconds: total night duration in seconds

    * return roounded off time to nearest minute
    """
    tm = time.gmtime(total_seconds)
    minutes = tm.tm_min
    hours = tm.tm_hour
    if tm.tm_sec > 30:
        minutes += 1
    if tm.tm_hour < 10:
        hours = "0" + str(tm.tm_hour)
    if minutes < 10:
        minutes = "0" + str(minutes)
    roundoff_time = str(hours) + ":" + str(minutes) + ":00"
    return roundoff_time


def calculate_night_hours(sunset_coordinates_list, sunrise_coordinates_list, travel_info,
                          start_datetime_obj, end_datetime_obj):
    """
    * Method to calculate night duration
    ***
        :param: sunset_coordinates_list - list of enroute sunset coordinates
        :param: sunrise_coordinates_list - list of enroute sunrise coordinates
        :param: travel_info - list of enroute sunset coordinates with sun's position
        :param: start_datetime_obj - start_datetime_obj
        :param: end_datetime_obj - end_datetime_obj
    * return total night duration
    """
    same_day = True if (end_datetime_obj - start_datetime_obj).days == 0 else False
    night_seconds, day_seconds = 0.0, 0.0

    if travel_info["start"] == "day" and travel_info["end"] == "day" and same_day:
        if sunset_coordinates_list and sunset_coordinates_list:
            night_seconds = (sunrise_coordinates_list[0]["datetime_of_sunrise"] - sunset_coordinates_list[0
            ]["datetime_of_sunset"]).seconds
    elif travel_info["start"] == "day" and travel_info["end"] == "day" and not same_day:
        if len(sunrise_coordinates_list) == 1 and len(sunset_coordinates_list) == 1:
            time_diff = (sunrise_coordinates_list[0]["datetime_of_sunrise"] - sunset_coordinates_list[0]["datetime_of_sunset"]).seconds
            night_seconds = (end_datetime_obj - sunset_coordinates_list[0]["datetime_of_sunset"]).seconds if time_diff > 0 else 0
        elif len(sunrise_coordinates_list) > 1 or len(sunset_coordinates_list) > 1:
            night_seconds = ((sunrise_coordinates_list[0]["datetime_of_sunrise"] - sunset_coordinates_list[0]["datetime_of_sunset"]) + (end_datetime_obj - sunset_coordinates_list[1]["datetime_of_sunset"])).seconds
    elif travel_info["start"] == "night" and travel_info["end"] == "night":
        if sunset_coordinates_list and sunrise_coordinates_list:
            day_seconds = (sunset_coordinates_list[0]["datetime_of_sunset"] - sunrise_coordinates_list[0]["datetime_of_sunrise"]).seconds
            night_seconds = travel_info["total_duration"] - day_seconds
        else:
            night_seconds = (end_datetime_obj - start_datetime_obj).seconds

    elif travel_info["start"] == "day" and travel_info["end"] == "night":
        if sunrise_coordinates_list and len(sunset_coordinates_list) > 1:
            night_seconds = ((sunrise_coordinates_list[0]["datetime_of_sunrise"] - sunset_coordinates_list[0]["datetime_of_sunset"]) + (end_datetime_obj- sunset_coordinates_list[1]["datetime_of_sunset"])).seconds
        else:
            night_seconds = (end_datetime_obj - sunset_coordinates_list[0]["datetime_of_sunset"]).seconds
    elif travel_info["start"] == "night" and travel_info["end"] == "day":
        if len(sunrise_coordinates_list) > 1 and sunset_coordinates_list:
            night_seconds = ((sunrise_coordinates_list[0]["datetime_of_sunrise"] - start_datetime_obj) + (sunrise_coordinates_list[1]["datetime_of_sunrise"] - sunset_coordinates_list[0]["datetime_of_sunset"])).seconds
        else:
            day_seconds = (end_datetime_obj - sunrise_coordinates_list[0]["datetime_of_sunrise"]).seconds
            night_seconds = travel_info["total_duration"] - day_seconds

    night_duration = get_roundoff_time(night_seconds)
    return night_duration


def process_positional_data(travel_info, start_datetime_obj, end_datetime_obj):
    """
    * Method to process coordinate wise data to find sunrise and sunset coordinates
    ***
        :params: travel_info - coordinates list with sun's position at points
        :params: start_datetime_obj: start_datetime_obj
        :params: end_datetime_obj: end_datetime_obj
    * return each coordinates's positional sun position data
    """
    sunset_coordinates_list = []
    sunrise_coordinates_list = []
    state = travel_info["start"]
    coordinates = travel_info["coordinates_list"]
    for point in coordinates:
        if state == "day" and point:
            if point["altitude"] < 0:
                state = "night"
                point["datetime_of_sunset"] = point["time_at_c"]
                point["sunrise_on_route"] = False
                point["sunset_on_route"] = True
                del point["azimuth"]
                del point["index"]
                del point["time_at_c"]
                sunset_coordinates_list.append(point)
        if state == "night":
            if point["altitude"] > 0:
                state = "day"
                point["datetime_of_sunrise"] = point["time_at_c"]
                point["sunrise_on_route"] = True
                point["sunset_on_route"] = False
                del point["azimuth"]
                del point["index"]
                del point["time_at_c"]
                sunrise_coordinates_list.append(point)
        del point["altitude"]

    travel_info["point_sunset_info"] = sunset_coordinates_list
    travel_info["point_sunrise_info"] = sunrise_coordinates_list
    travel_info["night_duration"] = calculate_night_hours(sunset_coordinates_list, sunrise_coordinates_list,
                                                          travel_info, start_datetime_obj, end_datetime_obj)
    del travel_info["coordinates_list"]

    return travel_info


def get_flight_route_data(start_latitide, start_longitude, start_datetime, end_latitude, end_longitude, end_datetime):
    """
    * Method to find sun's position during flight
    ***
        :params start_latitide : source's latitude
        :params start_longitude : source's longitude
        :params start_datetime : flight's departure time
        :params end_latitude : destination's latitude
        :params end_longitude : destination's latitude
        :params end_datetime : flight's arrival latitude

    * return formatted dict with flight's route information
    """
    day = False
    night = False
    coordinates_list = []

    # start point day/night finder
    start_datetime_obj = datetime.strptime(start_datetime, "%Y%m%dT%H:%M:%SZ")
    end_datetime_obj = datetime.strptime(end_datetime, "%Y%m%dT%H:%M:%SZ")
    tz_start_time = start_datetime_obj.astimezone(pytz.timezone("UTC"))
    tz_end_time = end_datetime_obj.astimezone(pytz.timezone("UTC"))

    # checking for sun's position at start point to get if flight started in day or night
    initial_sun_position = getPosition(tz_start_time, start_latitide, start_longitude)
    if initial_sun_position["altitude"] > 0:
        day = True

    # checking for sun's position at start point to get if flight ended in day or night
    final_sun_position = getPosition(tz_end_time, end_latitude, end_longitude)
    if final_sun_position["altitude"] > 0:
        night = True

    # distance between start and end point
    travel_distance = great_circle(lonlat(start_longitude, start_latitide),
                                   lonlat(end_longitude, end_latitude)).kilometers

    total_duration = (end_datetime_obj - start_datetime_obj).seconds

    speed = travel_distance/(total_duration/3600)
    travel_info = {
        "start": "day" if day else "night",
        "end": "day" if night else "night",
        "travel_distance": travel_distance,
        "total_duration": time.strftime('%H:%M:%S', time.gmtime((end_datetime_obj - start_datetime_obj).seconds)),
        "speed": speed/1.852
    }

    A = (start_latitide, start_longitude)  # Point A (lat, long)
    B = (end_latitude, end_longitude)  # Point B (lat, lon)
    speed = travel_distance/(total_duration/3600)

    # code for finding geopoints after every 10km
    points_inbetween_coordinates = math.floor(travel_distance / 10)

    enroute_coordinates = []

    for point in range(points_inbetween_coordinates+1):

        positional_data, time_at_c, coordinates = get_positional_data(A, B, speed, start_datetime_obj)
        A = coordinates
        start_datetime_obj = time_at_c
        positional_data["index"] = point
        positional_data["time_at_c"] = time_at_c
        positional_data["enroute_sunrise_lat"] = coordinates[0]
        positional_data["enroute_sunrise_long"] = coordinates[1]

        coordinates_list.append(positional_data)

        remaining_distance = great_circle(lonlat(coordinates[1], coordinates[0]),
                                          lonlat(end_longitude, end_latitude)).kilometers
        point += 1
        enroute_coordinates.append({"lat": A[0], "long": A[1]})
    travel_info["coordinates_list"] = coordinates_list
    travel_info["total_duration"] = (tz_end_time - tz_start_time).seconds
    final_results = process_positional_data(travel_info, tz_start_time, tz_end_time)
    final_results["total_duration"] = time.strftime('%H:%M:%S', time.gmtime((tz_end_time - tz_start_time).seconds))
    final_results["enroute_coordinates"] = enroute_coordinates
    return final_results

"""
    flight_locator controller file
"""
import math
import time
from datetime import datetime, timedelta

import pytz
from astral import LocationInfo
from astral.sun import sun
from geographiclib.geodesic import Geodesic
from geopy.distance import lonlat, great_circle
from rest_framework import status
from rest_framework.response import Response

from .suncalc_v2 import getTimes


def calculate_night_hours(start_datetime, end_datetime, travel_info, total_duration):
    """
    * returns 'night hours'
         * given the flight starts in day/night, flight ends in day/night, sunrise object during flight
         * sunset object during flight if any
         * @param travel_info - final coordin   ates of sunrise and sunset
         * @param flightStart
         * @param flightEnd
         * @param sunriseInfo
         * @param sunsetInfo
         * @return string
    """
    day_hours, night_hours = 0, 0
    start = travel_info["start"]
    end = travel_info["end"]
    start_datetime = datetime.strptime(start_datetime, "%Y%m%dT%H:%M:%SZ").astimezone(pytz.timezone("UTC"))
    end_datetime = datetime.strptime(end_datetime, "%Y%m%dT%H:%M:%SZ").astimezone(pytz.timezone("UTC"))
    same_day = True if (end_datetime - start_datetime).days == 0 else False

    # day -day on same day flight
    if start == 'day' and end == 'day' and same_day:
        if travel_info["point_sunset_info"] and travel_info["point_sunrise_info"]:
            night_hours = (
                    travel_info["point_sunrise_info"]["datetime_of_sunrise"
                    ] - travel_info["point_sunset_info"]["datetime_of_sunset"]).seconds
        else:
            night_hours = 0
    # day - day but different days flight
    elif start == "day" and end == "day" and not same_day:
        if travel_info["point_sunset_info"] and travel_info["point_sunrise_info"]:
            night_hours = (travel_info["point_sunrise_info"]["datetime_of_sunrise"
                           ] - travel_info["point_sunset_info"]["datetime_of_sunset"]).seconds
    # night - night flight
    elif start == "night" and end == "night":
        if travel_info["point_sunset_info"] and travel_info["point_sunrise_info"]:
            day_hours = (
                    travel_info["point_sunset_info"]["datetime_of_sunset"
                    ] - travel_info["point_sunrise_info"]["datetime_of_sunrise"]).seconds
            night_hours = (total_duration - day_hours)
        else:
            night_hours = (end_datetime - start_datetime).seconds

    # day - night flight
    elif start == "day" and end == "night":
        night_hours = (end_datetime - travel_info["point_sunset_info"]["datetime_of_sunset"]).seconds
    # Night - day flight
    elif start == "night" and end == "day":
        day_hours = end_datetime - travel_info["point_sunrise_info"]["datetime_of_sunrise"]
        night_hours = (total_duration - day_hours.seconds)

    return night_hours


def get_bearing(start_point, end_point):
    """
    method to calculate bearing between two coordinates
    : params start_point
    : params end_point
    returns bearing
    """
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


def get_point_sun_data(start_point, end_point, speed, start_datetime):
    """
    method to get sun's positions on a coordinate
    : params start_point
    : params end_point
    : params speed
    : params start_datetime
    return sun's positional information
    """
    is_sunset = False
    is_sunrise = False
    # Define the ellipsoid
    geod = Geodesic.WGS84
    night_hours = 0.0
    # azimuth between start and end points
    inv = geod.Inverse(start_point[0], start_point[1], end_point[0], end_point[1])

    bearing = get_bearing(start_point, end_point)

    s_in_km = 10
    s_in_meter = s_in_km * 1000

    # geocodes of 10km distant point
    dir = geod.Direct(start_point[0], start_point[1], bearing, s_in_meter)
    C = (dir['lat2'], dir['lon2'])

    # time to reach point C from A
    speed_in_kmph = float(speed) * 1.852

    c_reaching_time = s_in_km / speed_in_kmph

    # Time when flight reaches C
    time_at_c = start_datetime.astimezone(pytz.timezone("UTC")) + timedelta(hours=c_reaching_time)
    try:
        c_sun_data = getTimes(time_at_c, start_point[0], start_point[1])
        tz_sunrise = datetime.strptime(c_sun_data["sunrise"], "%Y-%m-%d %H:%M:%S").astimezone(pytz.timezone("UTC"))
        tz_sunrise_end = datetime.strptime(c_sun_data["sunriseEnd"], "%Y-%m-%d %H:%M:%S"
                                           ).astimezone(pytz.timezone("UTC"))
        tz_sunset = datetime.strptime(c_sun_data["sunsetStart"], "%Y-%m-%d %H:%M:%S").astimezone(pytz.timezone("UTC"))
        tz_sunset_end = datetime.strptime(c_sun_data["sunset"], "%Y-%m-%d %H:%M:%S").astimezone(pytz.timezone("UTC"))
        if tz_sunrise <= time_at_c <= tz_sunrise_end:
            is_sunrise = True
        if tz_sunset <= time_at_c <= tz_sunset_end:
            is_sunset = True
    except (ValueError, TypeError):
        pass

    return C, time_at_c, is_sunset, is_sunrise


def get_flight_route_data(start_lat, start_long, start_datetime, end_lat, end_long, end_datetime, speed):
    """
    method to find sun's position during flight
    :params start_lat : source's latitude
    :params start_long : source's longitude
    :params start_datetime : flight's departure time
    :params end_lat : destination's latitude
    :params end_long : destination's latitude
    :params end_datetime : flight's arrival latitude
    :params speed : speed of flight

    return formatted dict with flight's route information
    """
    sunset_info = []
    sunrise_info = []
    # start point day/night finder
    start_datetime_obj = datetime.strptime(start_datetime, "%Y%m%dT%H:%M:%SZ")
    tz_start_time = start_datetime_obj.astimezone(pytz.timezone("UTC"))
    start_loc_info = LocationInfo(timezone="UTC",
                                  latitude=start_lat,
                                  longitude=start_long)
    sun_data = sun(start_loc_info.observer, date=start_datetime_obj)
    is_night = tz_start_time < sun_data["sunrise"] or tz_start_time > sun_data["dusk"]

    # end point day/night finder
    end_datetime_obj = datetime.strptime(end_datetime, "%Y%m%dT%H:%M:%SZ")
    tz_end_time = end_datetime_obj.astimezone(pytz.timezone("UTC"))
    end_loc_info = LocationInfo(timezone="UTC",
                                latitude=end_lat,
                                longitude=end_long)
    # sun position data
    end_sun_data = sun(end_loc_info.observer, date=end_datetime_obj)

    # is night
    end_is_night = tz_end_time < end_sun_data["sunrise"] or tz_end_time > end_sun_data["dusk"]

    # distance between start and end point
    travel_distance = great_circle(lonlat(start_long, start_lat),
                                   lonlat(end_long, end_lat)).kilometers

    total_duration = (end_datetime_obj - start_datetime_obj).seconds
    travel_info = {
        "start": "night" if bool(is_night) else "day",
        "end": "night" if bool(end_is_night) else "day",
        "travel_distance": travel_distance,
        "total_duration": time.strftime('%H:%M:%S', time.gmtime((end_datetime_obj - start_datetime_obj).seconds))
    }

    A = (start_lat, start_long)  # Point A (lat, lon)
    B = (end_lat, end_long)  # Point B (lat, lon)

    # code for finding geopoints after every 10km
    points_inbetween_coordinates = math.floor(travel_distance / 10)

    for point in range(points_inbetween_coordinates+1):
        info = {}
        sunset_sunrise_data, c_time, is_sunset, is_sunrise = get_point_sun_data(A, B, speed, start_datetime_obj)
        start_datetime_obj = c_time
        A = sunset_sunrise_data
        if is_sunset:
            info["enroute_sunset_lat"] = sunset_sunrise_data[0]
            info["enroute_sunset_long"] = sunset_sunrise_data[1]
            info["datetime_of_sunset"] = c_time
            info["sunrise_on_route"] = is_sunrise
            info["sunset_on_route"] = is_sunset
            sunset_info.append(info)

        if is_sunrise:
            info["enroute_sunrise_lat"] = sunset_sunrise_data[0]
            info["enroute_sunrise_long"] = sunset_sunrise_data[1]
            info["datetime_of_sunrise"] = c_time
            info["sunrise_on_route"] = is_sunrise
            info["sunset_on_route"] = is_sunset
            sunrise_info.append(info)

        # remaining_distance = great_circle(lonlat(sunset_sunrise_data[1], sunset_sunrise_data[0]),
        #                                   lonlat(end_long, end_lat)).kilometers
        # print("remaining_distance --- ", remaining_distance)
        point += 1
    travel_info["point_sunset_info"] = sunset_info[-1] if sunset_info else sunset_info
    travel_info["point_sunrise_info"] = sunrise_info[0] if sunrise_info else sunrise_info
    night_hours = calculate_night_hours(start_datetime, end_datetime, travel_info, total_duration)
    travel_info["night_hours"] = time.strftime('%H:%M', time.gmtime(night_hours))
    return travel_info

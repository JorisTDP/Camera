#!python3.9
# Math library used in geographic calculations
import math

def calculate_desired_compass_bearing(a: tuple, b: tuple) -> float:
    """
    Parameters
    ----------
    a : tuple
        A tuple containing the lat and long of point a
    b : tuple
        A tuple containing the lat and long of point b
    """
    
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])

    diff_long = math.radians(b[1] - a[1])

    # Determine the x and y distance between the two points
    delta_y = math.sin(diff_long) * math.cos(lat2)

    delta_x = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diff_long))

    bearing = math.atan2(delta_y, delta_x)

    # The atan2 function returns a value between -180 and 180. The value is
    # of little use in this form so should be converted into a 0-360 range.
    bearing = math.degrees(bearing)
    compass_bearing = (bearing + 360) % 360

    return compass_bearing

def calculate_distance_to_target(a: tuple, b: tuple) -> float:
    """
    Parameters
    ----------
    a : tuple
        A tuple containing the lat and long of point a
    b : tuple
        A tuple containing the lat and long of point b
    """

    R = 6371000
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])

    delta_lat = math.radians(b[0] - a[0])
    delta_lon = math.radians(b[1] - a[1])

    a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon/2) * math.sin(delta_lon/2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Distance in meters
    distance = R * c

    return distance

def calculate_next_position(target: tuple) -> tuple:
    """
    Parameters
    ----------
    target : tuple
        A tuple containing the lat, long, speed and bearing of a target
    """
    R = 6371000
    lat1 = math.radians(target[0])
    lon1 = math.radians(target[1])
    d = target[2]
    bearing = math.radians(target[3])

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(bearing) )
    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    return (math.degrees(lat2), math.degrees(lon2))
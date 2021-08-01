import requests
import numpy as np
import math

# Open street map overpass API URL
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Conventional Earth radius in meters
EARTH_RADIUS = 6378137.

def get_pass_from_osm(bbox):
    """
        Return points corresponding to mountain pass in a given bounding box
        from openstreetmap.
        
        :param bbox: bounding box, bbox[0] is bottom left corner, [0] is lat, [1] is lon, bbox[1] is top right corner
        
        :return: list of points
    """
    
    poly_definition = 'poly:"'+str(bbox[1][0])+' '+str(bbox[0][1])+' '+ \
                            str(bbox[1][0])+' '+str(bbox[1][1])+' '+ \
                            str(bbox[0][0])+' '+str(bbox[1][1])+' '+ \
                            str(bbox[0][0])+' '+str(bbox[0][1])+'"'
    
    overpass_query = """
    [out:json][timeout:60];
    (node["mountain_pass"="yes"]("""+poly_definition+""");
    node["natural"="saddle"]("""+poly_definition+""");
    );
    out center;
    """
    
    # TODO verify if is really needed
    header = {'User-agent': 'Test App'}
    
    res = requests.get(OVERPASS_URL, params={'data': overpass_query},
                       headers=header)
    
    if res.status_code == 200:
        # Request is successfull
        data = res.json()
        cols = []
        for element in data['elements']:
            col = {}
            col['lat'] = element['lat']
            col['lon'] = element['lon']
            col['osmid'] = element['id']
            if 'name' in element['tags']:
                col['name'] = element['tags']['name'] 
        
            if 'ele' in element['tags']:
                try:
                    col['ele'] = float(element['tags']['ele'])
                except:
                    print("Cannot convert " + element['tags']['ele'] + " to Float")

            cols.append(col)
        
        return cols
    
    elif res.status_code == 429:
        # Too large zone, divide it in 4
        cols = []
        clat = (bbox[0][0]+bbox[1][0])/2.
        clon = (bbox[0][1]+bbox[1][1])/2.
        bbox_tl = [[clat, bbox[0][1]],
                   [bbox[1][0], clon]]
        bbox_tr = [[clat, clon],
                   [bbox[1][0], bbox[1][1]]]
        bbox_bl = [[bbox[0][0], bbox[0][1]],
                   [clat, clon]]
        bbox_br = [[bbox[0][0], clon],
                   [clat, bbox[1][1]]]
        cols = cols + get_pass_from_osm(bbox_tl)
        cols = cols + get_pass_from_osm(bbox_tr)
        cols = cols + get_pass_from_osm(bbox_bl)
        cols = cols + get_pass_from_osm(bbox_br)
        # remove doubles (there should be none)
        #cols = list(set(cols))
        return cols

    else:
        # Not handled
        print("ERROR CODE : "+str(res.status_code))
        # Just retry
        return get_pass_from_osm(bbox)

def distance(lat_a, lon_a, lat_b, lon_b):
    """
        Return distance in meters between two points A and B 
        with given latiude and longitude in degree.
        
        :param lat_a: latitude of point A in degrees
        :param lon_a: longitude of point A in degrees
        :param lat_b: latitude of point B in degrees
        :param lon_b: longitude of point B in degrees
        
        :return: distance betweeen points A and B in meters
    """
    
    #TODO : remplacer la conversion par math.radians
    
    lat_a_rad = lat_a*np.pi/180.
    lon_a_rad = lon_a*np.pi/180.
    lat_b_rad = lat_b*np.pi/180.
    lon_b_rad = lon_b*np.pi/180.

        
    return EARTH_RADIUS*np.arccos(np.sin(lat_a_rad)*np.sin(lat_b_rad) + np.cos(lat_a_rad)*np.cos(lat_b_rad)*np.cos(lon_b_rad-lon_a_rad))   

def point_in_line(lat_a, lon_a, lat_b, lon_b, lat_c, lon_c, tol):
    """
        Check distance from a point C to a line AB
        if distance < tol return true
        
        :param lat_a: latitude of point A in degrees
        :param lon_a: longitude of point A in degrees
        :param lat_b: latitude of point B in degrees
        :param lon_b: longitude of point B in degrees
        :param lat_c: latitude of point C in degrees
        :param lon_c: longitude of point C in degrees
        :param tol: tolerance in meters
        
        :return True if distance is inferior to tolerance, False otherwise
    """

    
    if distance(lat_a, lon_a, lat_c, lon_c) <= tol:
        return True
    if distance(lat_b, lon_b, lat_c, lon_c) <= tol:
        return True
    
    if distance(lat_a, lon_a, lat_b, lon_b) >= tol/2.: # On pourrait aussi tester juste > tol
        lat_d = (lat_a+lat_b)/2.
        lon_d = (lon_a+lon_b)/2.
        return point_in_line(lat_a, lon_a, lat_d, lon_d, lat_c, lon_c, tol) or point_in_line(lat_d, lon_d, lat_b, lon_b, lat_c, lon_c, tol)


    return False

def point_in_polyline(poly, lat_c, lon_c, tol):
    """
        Check if a point belong to a polyline with tol
    
        :param poly: polyline containing coordinates in degrees
        :param lat_c: latitude of point C in degrees
        :param lon_c: longitude of point C in degrees
        :param tol: tolerance in meters
        
        :return True if point belong to polyline, False otherwise
    """
    
    for i_point in range(np.shape(poly)[0]-1):
        if point_in_line(poly[i_point, 0], poly[i_point, 1], poly[i_point+1, 0], poly[i_point+1, 1],lat_c, lon_c, tol):
            return True
        
    return False

def deg2num(lat_deg, lon_deg, zoom):
    """Compute OSM tile number from lon/lat"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int(n*(lon_deg + 180.0) / 360.0)
    ytile = int(n*(1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    """Return the NW corner of a given OSM tile in degrees"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def visited_tiles_in_polyline(poly, zoom):
    """
        Check tiles visited by a polyline
        
        :param poly: polyline containing coordinates in degrees
        :param zoom: zoom level to perform search
        
        :return Array of visited tiles
    """
    visited_full = np.zeros((np.shape(poly)[0], 3), dtype=int)
    for i_point in range(np.shape(poly)[0]):
        visited_full[i_point,:2] = deg2num(poly[i_point,0],poly[i_point,1], zoom)
        visited_full[i_point, 2] = zoom
        
    return np.unique(visited_full, axis=0)
        
        

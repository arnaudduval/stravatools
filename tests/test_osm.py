import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from stravatools import osmtools

c = osmtools.get_pass_from_osm([[40., 0.],[45., 53.]])

print(c)

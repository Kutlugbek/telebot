import sqlite3
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
	# Function to calculate the distance between two points using Haversine formula
	R = 6371  # Radius of the Earth in kilometers

	dlat = radians(lat2 - lat1)
	dlon = radians(lon2 - lon1)

	a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c  # Distance in kilometers
	return distance
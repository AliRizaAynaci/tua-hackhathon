#!/usr/bin/env python3
import sys
import subprocess
import rasterio
import math

if len(sys.argv) < 6:
    print("Usage: python3 crop_tiff.py <input.tif> <x> <y> <width> <height> <output.tif>")
    sys.exit(1)

input_tif = sys.argv[1]
x, y, width, height = map(int, sys.argv[2:6])
output_tif = sys.argv[6]

cmd = [
    "gdal_translate", "-srcwin", str(x), str(y), str(width), str(height),
    input_tif, output_tif
]
subprocess.run(cmd)

with rasterio.open(output_tif) as ds:
    bounds = ds.bounds
    
    R = 1737400
    phi1 = math.radians(28)
    
    def meters_to_latlon(x, y):
        lat = math.degrees(y / R)
        lon = math.degrees(x / (R * math.cos(phi1)))
        return lat, lon
    
    lat_ul, lon_ul = meters_to_latlon(bounds.left, bounds.top)
    lat_ur, lon_ur = meters_to_latlon(bounds.right, bounds.top)
    lat_ll, lon_ll = meters_to_latlon(bounds.left, bounds.bottom)
    lat_lr, lon_lr = meters_to_latlon(bounds.right, bounds.bottom)
    lat_c, lon_c = meters_to_latlon((bounds.left+bounds.right)/2, (bounds.top+bounds.bottom)/2)
    
    def fmt_coord(lat, lon):
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "W" if lon <= 0 else "E"
        return f"{abs(lat):.5f}{lat_dir}, {abs(lon):.5f}{lon_dir}"
    
    print(f"\nCoordinates:")
    print(f"  Upper Left:  {fmt_coord(lat_ul, lon_ul)}")
    print(f"  Upper Right: {fmt_coord(lat_ur, lon_ur)}")
    print(f"  Lower Left:  {fmt_coord(lat_ll, lon_ll)}")
    print(f"  Lower Right: {fmt_coord(lat_lr, lon_lr)}")
    print(f"  Center:      {fmt_coord(lat_c, lon_c)}")

print(f"\nDone: {output_tif}")

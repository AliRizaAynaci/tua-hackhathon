#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import rasterio
import sys

if len(sys.argv) < 2:
    print("Usage: python3 tif2png.py <input.tif> [output.png]")
    sys.exit(1)

input_tif = sys.argv[1]
output_png = sys.argv[2] if len(sys.argv) > 2 else input_tif.replace('.tif', '.png')

with rasterio.open(input_tif) as ds:
    dem = ds.read(1)
    bounds = ds.bounds
    nodata = ds.nodata

dem_filtered = np.where(dem == nodata, np.nan, dem)

ls = LightSource(azdeg=315, altdeg=45)
hillshade = ls.hillshade(dem_filtered)

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
axes[0].imshow(dem_filtered, cmap='gray')
axes[0].set_title(f'Raw DEM ({dem.shape[1]}x{dem.shape[0]})\n{bounds}')
axes[0].axis('off')

axes[1].imshow(hillshade, cmap='gray')
axes[1].set_title('Hillshade')
axes[1].axis('off')

plt.tight_layout()
plt.savefig(output_png, dpi=100)
print(f"Done: {output_png}")

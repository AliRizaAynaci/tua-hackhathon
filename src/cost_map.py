#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import rasterio
from scipy.ndimage import generic_filter
import sys
import os
import argparse

def calculate_slope(dem, resolution=1.5):
    """
    Calculates the slope of the DEM in degrees using numpy gradient.
    This is faster and more accurate than looping.
    """
    # Calculate gradient in y and x directions
    dy, dx = np.gradient(dem, resolution, resolution)
    
    # Calculate slope in degrees
    slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
    
    return slope

def calculate_roughness(dem, window=3):
    """
    Calculates the roughness (standard deviation of elevation in a local window).
    """
    def roughness_func(values):
        valid_values = values[~np.isnan(values)]
        if len(valid_values) < 2:
            return np.nan
        return np.std(valid_values)
    
    roughness = generic_filter(dem, roughness_func, size=window, mode='constant', cval=np.nan)
    return roughness

def create_cost_map(dem, slope, roughness, max_slope=30, max_roughness=2, slope_weight=1.0, roughness_weight=0.5):
    cost_map = np.full_like(dem, np.nan, dtype=np.float32)
    obstacle_mask = np.zeros_like(dem, dtype=bool)
    
    obstacle_mask |= slope > max_slope
    obstacle_mask |= roughness > max_roughness
    obstacle_mask |= np.isnan(dem)
    obstacle_mask |= np.isnan(slope)
    obstacle_mask |= np.isnan(roughness)
    
    valid = ~obstacle_mask
    slope_norm = np.clip(slope[valid] / max_slope, 0, 1)
    roughness_norm = np.clip(roughness[valid] / max_roughness, 0, 1)
    
    cost_map[valid] = slope_norm * slope_weight + roughness_norm * roughness_weight
    
    cost_map[obstacle_mask] = 1.0
    
    return cost_map, obstacle_mask

def visualize(cost_map, slope, roughness, output_prefix="cost_map"):
    colors = ['#00ff00', '#ffff00', '#ff0000']
    cmap = LinearSegmentedColormap.from_list('cost', colors)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    axes[0, 0].imshow(slope, cmap='terrain', vmin=0, vmax=30)
    axes[0, 0].set_title('Slope (degrees)')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(roughness, cmap='viridis', vmin=0, vmax=2)
    axes[0, 1].set_title('Roughness (meters)')
    axes[0, 1].axis('off')
    
    im = axes[1, 0].imshow(cost_map, cmap=cmap, vmin=0, vmax=1)
    axes[1, 0].set_title('Cost Map (0=free, 1=blocked)')
    axes[1, 0].axis('off')
    plt.colorbar(im, ax=axes[1, 0], label='Cost')
    
    obstacle_viz = np.where(np.isnan(cost_map), 0.5, cost_map)
    axes[1, 1].imshow(obstacle_viz, cmap=cmap, vmin=0, vmax=1)
    axes[1, 1].set_title('Obstacle Map (red=blocked)')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}.png', dpi=100)
    print(f"Saved: {output_prefix}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create cost map from DEM")
    parser.add_argument("input_tif", help="Input DEM file (.tif)")
    parser.add_argument("output_prefix", nargs="?", default="cost_map", help="Output prefix (default: cost_map)")
    parser.add_argument("--max-slope", type=float, default=30, help="Max slope in degrees (default: 30)")
    parser.add_argument("--max-roughness", type=float, default=2, help="Max roughness in meters (default: 2)")
    parser.add_argument("--slope-weight", type=float, default=1.0, help="Slope weight (default: 1.0)")
    parser.add_argument("--roughness-weight", type=float, default=0.5, help="Roughness weight (default: 0.5)")
    parser.add_argument("--roughness-window", type=int, default=3, help="Roughness window size (default: 3)")
    
    args = parser.parse_args()
    
    print("Loading DEM...")
    with rasterio.open(args.input_tif) as ds:
        dem = ds.read(1)
        nodata = ds.nodata
        resolution = abs(ds.transform[0])
    
    dem = np.where(dem == nodata, np.nan, dem)
    print(f"  DEM shape: {dem.shape}")
    print(f"  Resolution: {resolution}m")
    
    print(f"\nParameters:")
    print(f"  max_slope: {args.max_slope}°")
    print(f"  max_roughness: {args.max_roughness}m")
    print(f"  slope_weight: {args.slope_weight}")
    print(f"  roughness_weight: {args.roughness_weight}")
    
    print("\nCalculating slope...")
    slope = calculate_slope(dem, resolution)
    print(f"  Slope range: {np.nanmin(slope):.1f} - {np.nanmax(slope):.1f} degrees")
    
    print("\nCalculating roughness...")
    roughness = calculate_roughness(dem, window=args.roughness_window)
    print(f"  Roughness range: {np.nanmin(roughness):.2f} - {np.nanmax(roughness):.2f} m")
    
    print("\nCreating cost map...")
    cost_map, obstacles = create_cost_map(
        dem, slope, roughness,
        max_slope=args.max_slope,
        max_roughness=args.max_roughness,
        slope_weight=args.slope_weight,
        roughness_weight=args.roughness_weight
    )
    obstacle_pct = (obstacles & ~np.isnan(dem)).sum() / (~np.isnan(dem)).sum() * 100
    print(f"  Obstacles: {obstacle_pct:.1f}%")
    
    print("\nVisualizing...")
    visualize(cost_map, slope, roughness, args.output_prefix)
    
    print("\nSaving numpy arrays...")
    os.makedirs(args.output_prefix + "_data", exist_ok=True)
    np.save(f'{args.output_prefix}_data/cost_map.npy', cost_map)
    np.save(f'{args.output_prefix}_data/slope.npy', slope)
    np.save(f'{args.output_prefix}_data/roughness.npy', roughness)
    print(f"  Saved to {args.output_prefix}_data/")
    
    print("\nDone!")

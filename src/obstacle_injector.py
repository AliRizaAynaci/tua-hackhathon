import numpy as np
import os
import argparse

def inject_obstacles(cost_map_path, output_path, num_obstacles=5, min_radius=10, max_radius=30, obstacle_cost=1.0):
    """
    Reads an existing cost map (.npy), injects random circular obstacles,
    and saves the new map.
    """
    if not os.path.exists(cost_map_path):
        print(f"Error: {cost_map_path} not found.")
        return
        
    print(f"Loading baseline cost map from {cost_map_path}...")
    cost_map = np.load(cost_map_path)
    new_cost_map = cost_map.copy()
    
    rows, cols = cost_map.shape
    added = 0
    
    # Simple RNG seed for reproducibility in testing (optional)
    # np.random.seed(42)
    
    while added < num_obstacles:
        # Pick random center
        cy = np.random.randint(0, rows)
        cx = np.random.randint(0, cols)
        
        # Pick random radius
        r = np.random.randint(min_radius, max_radius)
        
        # Skip if center is already an obstacle or NaN
        if np.isnan(cost_map[cy, cx]) or cost_map[cy, cx] >= obstacle_cost:
            continue
            
        # Create a circular mask
        y, x = np.ogrid[-cy:rows-cy, -cx:cols-cx]
        mask = x**2 + y**2 <= r**2
        
        # Apply obstacle
        new_cost_map[mask] = obstacle_cost
        added += 1
        print(f"  Injected obstacle {added}/{num_obstacles} at ({cx}, {cy}) with radius {r}")
        
    np.save(output_path, new_cost_map)
    print(f"Saved new cost map to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject obstacles into a cost map")
    parser.add_argument("input", help="Input cost map (.npy)")
    parser.add_argument("output", help="Output new cost map (.npy)")
    parser.add_argument("--num", type=int, default=5, help="Number of obstacles")
    parser.add_argument("--min-r", type=int, default=10, help="Min radius in pixels")
    parser.add_argument("--max-r", type=int, default=30, help="Max radius in pixels")
    
    args = parser.parse_args()
    inject_obstacles(args.input, args.output, args.num, args.min_r, args.max_r)

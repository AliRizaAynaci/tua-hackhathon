# 🌕 Lunar Rover Navigation Pipeline

## 📌 Overview

This project simulates autonomous navigation of a lunar rover on the Moon's surface. The system combines **global path planning** using elevation data and **local obstacle avoidance** similar to real-world rover systems.

---

## 🧠 Core Concept

The system is divided into two main parts:

1. **Global Planning (Offline)**
2. **Local Navigation (Real-time)**

---

## 🧭 Pipeline Architecture

```
DEM (TIFF)
   ↓
Slope Map (Terrain steepness)
   ↓
Cost Map (Traversability)
   ↓
A* Path Planning
   ↓
Waypoints (Path)
   ↓
Rover Execution + Local Obstacle Avoidance
```

---

## 📂 Step-by-Step Explanation

### 1. DEM (Digital Elevation Model)

* Input data in `.tif` format
* Each pixel represents elevation (height)

---

### 2. Region of Interest (ROI)

Instead of processing the entire Moon:

* A smaller region is selected
* This improves performance and mimics real rover constraints

---

### 3. Slope Map

Slope is computed from elevation differences:

```python
dx = np.gradient(dem, axis=1)
dy = np.gradient(dem, axis=0)
slope = np.sqrt(dx**2 + dy**2)
```

👉 Interpretation:

* Low slope → flat terrain (safe)
* High slope → steep terrain (danger)

---

### 4. Cost Map

Slope is converted into movement cost:

```python
cost_map = 1 + slope * k
```

Or threshold-based:

```python
obstacle = slope > threshold
```

---

### 5. Path Planning (A*)

A* algorithm computes optimal path:

* Input:

  * cost_map
  * start point
  * goal point

* Output:

```python
path = [(x1,y1), (x2,y2), ...]
```

---

### 6. Rover Execution

Rover receives only:

* Path (waypoints)

It does NOT receive:

* Full map ❌

---

### 7. Local Navigation (Real-time)

During movement:

* Rover uses sensors (simulated LiDAR / camera)
* Detects obstacles
* Adjusts path dynamically

```python
if obstacle_detected:
    avoid_obstacle()
    rejoin_path()
```

---

## 🧠 Key Insight

> Global planning tells the rover **where to go**
> Local navigation determines **how to go**

---

## 🚀 Scaling Strategy

Start small:

* 500x500 or 1000x1000 DEM

Then scale:

* Larger regions
* Tiling system for full Moon coverage

---

## ⚠️ Important Notes

* Full Moon DEM is too large for direct processing
* Always use ROI (cropping/windowing)
* Slope is more important than raw elevation

---

## 🧪 Current Progress

✔ DEM cropping
✔ DEM visualization (hillshade)
✔ Slope map generation
✔ Cost map
🔜 A* path planning
🔜 Local obstacle avoidance

---

## 🎯 Goal

Simulate a rover that:

* Plans a path using terrain data
* Navigates safely
* Avoids obstacles in real-time

---

## 🛠️ Tech Stack

* Python (NumPy, Rasterio, Matplotlib)
* GDAL (for TIFF processing)
* Unity (optional, for simulation)

---

## 📌 Future Work

* Real-time sensor simulation
* Dynamic replanning
* Unity integration
* Multi-resolution mapping

---

## 🧠 Final Thought

> A rover does not need the whole world.
> It only needs to know where to go — and how to survive getting there.

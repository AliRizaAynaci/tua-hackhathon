import numpy as np
import heapq
import math
import random

class AStarPlanner:
    def __init__(self, cost_map, obstacle_threshold=0.8):
        self.cost_map = cost_map
        self.rows, self.cols = cost_map.shape
        self.obstacle_threshold = obstacle_threshold
        # 8-connected grid
        self.motions = [
            (0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1),
            (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
            (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))
        ]

    def heuristic(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def is_valid(self, r, c):
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return False
        if np.isnan(self.cost_map[r, c]) or self.cost_map[r, c] >= self.obstacle_threshold:
            return False
        return True

    def plan(self, start, goal, safety_weight=10.0, max_danger=0.8):
        sr, sc = int(start[1]), int(start[0])
        gr, gc = int(goal[1]), int(goal[0])
        
        # Aggressive mode (fuel saving) means we tolerate more danger.
        old_thresh = self.obstacle_threshold
        self.obstacle_threshold = max_danger
        
        if not self.is_valid(sr, sc):
            print("Start node is invalid.")
            self.obstacle_threshold = old_thresh
            return None
        if not self.is_valid(gr, gc):
            print("Goal node is invalid.")
            self.obstacle_threshold = old_thresh
            return None

        open_set = []
        heapq.heappush(open_set, (0.0, sr, sc))
        
        came_from = {}
        g_score = {(sr, sc): 0.0}
        
        while open_set:
            _, cr, cc = heapq.heappop(open_set)
            
            if cr == gr and cc == gc:
                # Reconstruct path
                path = []
                curr = (cr, cc)
                while curr in came_from:
                    path.append((curr[1], curr[0])) # (x, y)
                    curr = came_from[curr]
                path.append((sc, sr))
                path.reverse()
                self.obstacle_threshold = old_thresh
                return path
                
            for dr, dc, dist in self.motions:
                nr, nc = cr + dr, cc + dc
                if not self.is_valid(nr, nc):
                    continue
                
                # Dynamic cost: distance + map penalty
                step_cost = dist + (self.cost_map[nr, nc] * dist * safety_weight)
                tentative_g = g_score[(cr, cc)] + step_cost
                
                if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                    g_score[(nr, nc)] = tentative_g
                    f_score = tentative_g + self.heuristic((nc, nr), (gc, gr))
                    heapq.heappush(open_set, (f_score, nr, nc))
                    came_from[(nr, nc)] = (cr, cc)
                    
        print("A* failed to find a path.")
        self.obstacle_threshold = old_thresh
        return None

class RRTPlanner:
    def __init__(self, cost_map, obstacle_threshold=0.8, step_size=5.0, goal_sample_rate=0.1, max_iter=2000):
        self.cost_map = cost_map
        self.rows, self.cols = cost_map.shape
        self.obstacle_threshold = obstacle_threshold
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter

    class Node:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.parent = None

    def is_collision_free(self, node_from, node_to):
        """Line of sight check via sampling."""
        steps = int(math.hypot(node_to.x - node_from.x, node_to.y - node_from.y) * 2)
        if steps == 0:
            return True
            
        for i in range(steps + 1):
            t = i / steps
            x = int(node_from.x + t * (node_to.x - node_from.x))
            y = int(node_from.y + t * (node_to.y - node_from.y))
            
            if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
                return False
            if np.isnan(self.cost_map[y, x]) or self.cost_map[y, x] >= self.obstacle_threshold:
                return False
        return True

    def get_nearest_node_index(self, node_list, rnd_node):
        dlist = [(node.x - rnd_node.x)**2 + (node.y - rnd_node.y)**2 for node in node_list]
        return dlist.index(min(dlist))

    def plan(self, start, goal):
        start_node = self.Node(start[0], start[1])
        goal_node = self.Node(goal[0], goal[1])
        node_list = [start_node]
        
        for i in range(self.max_iter):
            # Sample random node
            if random.random() > self.goal_sample_rate:
                rnd_node = self.Node(random.uniform(0, self.cols-1), random.uniform(0, self.rows-1))
            else:
                rnd_node = self.Node(goal_node.x, goal_node.y)
                
            # Find nearest node
            nearest_ind = self.get_nearest_node_index(node_list, rnd_node)
            nearest_node = node_list[nearest_ind]
            
            # Steer
            theta = math.atan2(rnd_node.y - nearest_node.y, rnd_node.x - nearest_node.x)
            new_node = self.Node(nearest_node.x + self.step_size * math.cos(theta),
                                 nearest_node.y + self.step_size * math.sin(theta))
            new_node.parent = nearest_node
            
            # Check collision
            if self.is_collision_free(nearest_node, new_node):
                node_list.append(new_node)
                
                # Check if reached goal
                d = math.hypot(new_node.x - goal_node.x, new_node.y - goal_node.y)
                if d <= self.step_size:
                    if self.is_collision_free(new_node, goal_node):
                        goal_node.parent = new_node
                        node_list.append(goal_node)
                        return self.generate_final_course(goal_node)
                        
        print("RRT failed to find a path within max_iter.")
        return None

    def generate_final_course(self, goal_node):
        path = [[goal_node.x, goal_node.y]]
        node = goal_node
        while node.parent is not None:
            node = node.parent
            path.append([node.x, node.y])
        path.reverse()
        return path

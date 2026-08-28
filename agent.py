# agent.py

import random
from collections import deque
import heapq
import math

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    # Practical 04 - Task 1.3
    # Initialize A* agent
    def __init__(self):
        self.active_algo = 'AStar'
        self.plan = []

    # Task 3 - BFS
    # FIFO Queue - explores shallow nodes first
    def bfs_search(self, graph, start, goal):
        queue = deque([(start, [start])])
        
        # Task 6 - visited states
        reached = {start}

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in reached:
                    reached.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None


    # Task 4 - DFS
    # LIFO Stack - explores deep nodes first
    def dfs_search(self, graph, start, goal):
        stack = [(start, [start])]
        
        # Task 6 - visited states
        reached = {start}

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in reached:
                    reached.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

        return None


    # Task 5 - UCS
    # Priority Queue - lowest cost first
    def ucs_search(self, graph, start, goal):
        priority_queue = [(0, start, [start])]
        
        # Task 6 - visited states
        reached = set()

        while priority_queue:
            cost, current, path = heapq.heappop(priority_queue)

            if current in reached:
                continue

            reached.add(current)

            if current == goal:
                return path, cost

            for neighbor, step_cost in graph.get(current, []):
                if neighbor not in reached:
                    new_cost = cost + step_cost

                    heapq.heappush(
                        priority_queue,
                        (new_cost, neighbor, path + [neighbor])
                    )

        return None

    # Practical 04 - Task 1.1
    # Manhattan Distance Heuristic
    def manhattan_distance(self, pos, goal):
        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)


    # Practical 04 - Task 1.1
    # Euclidean Distance Heuristic
    def euclidean_distance(self, pos, goal):
        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )

    # Practical 04 - Task 1.2
    # A* Search using f(n) = g(n) + h(n)
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        priority_queue = []
        reached_states = set()

        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        g_cost = 0
        h_cost = heuristic(start_pos, goal_pos)
        f_cost = g_cost + h_cost

        heapq.heappush(
            priority_queue,
            (f_cost, g_cost, start_pos, [start_pos])
        )

        width, height = grid_size

        while priority_queue:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                priority_queue
            )

            if current_pos in reached_states:
                continue

            if current_pos == goal_pos:
                return path_taken

            reached_states.add(current_pos)

            x, y = current_pos

            neighbors = [
                (x, y + 1),
                (x, y - 1),
                (x - 1, y),
                (x + 1, y)
            ]

            for neighbor in neighbors:

                nx, ny = neighbor

                if nx < 0 or nx >= width:
                    continue

                if ny < 0 or ny >= height:
                    continue

                if neighbor in walls:
                    continue

                if neighbor in reached_states:
                    continue

                new_g = g_cost + 1
                new_h = heuristic(neighbor, goal_pos)
                new_f = new_g + new_h

                heapq.heappush(
                    priority_queue,
                    (
                        new_f,
                        new_g,
                        neighbor,
                        path_taken + [neighbor]
                    )
                )

        return None

    # Practical 04 - Task 1.3
    # Integrate BFS, DFS, UCS and A* into the agent decision loop
    def sense_and_act(self, percept: dict):

        if self.plan:
            return self.plan.pop(0)

        current_pos = tuple(
            percept['agent_pos']
        )

        walls = set(
            tuple(wall)
            for wall in percept['walls']
        )

        grid_size = percept['grid_size']

        remaining_food = [
            tuple(food)
            for food in percept['all_food']
        ]

        if not remaining_food:

            return random.choice(
                ['Up', 'Down', 'Left', 'Right']
            )

        # Find closest food
        goal_pos = min(
            remaining_food,
            key=lambda food:
                self.manhattan_distance(
                    current_pos,
                    food
                )
        )

        width, height = grid_size

        # Create grid graph
        graph = {}

        for x in range(width):

            for y in range(height):

                current = (x, y)

                if current in walls:
                    continue

                neighbors = [
                    (x, y + 1),
                    (x, y - 1),
                    (x - 1, y),
                    (x + 1, y)
                ]

                valid_neighbors = []

                for neighbor in neighbors:

                    nx, ny = neighbor

                    if (
                        0 <= nx < width
                        and
                        0 <= ny < height
                        and
                        neighbor not in walls
                    ):

                        valid_neighbors.append(
                            neighbor
                        )

                graph[current] = valid_neighbors

        path = None

        # BFS
        if self.active_algo == 'BFS':

            path = self.bfs_search(
                graph,
                current_pos,
                goal_pos
            )

        # DFS
        elif self.active_algo == 'DFS':

            path = self.dfs_search(
                graph,
                current_pos,
                goal_pos
            )

        # UCS
        elif self.active_algo == 'UCS':

            weighted_graph = {}

            for node, neighbors in graph.items():

                weighted_graph[node] = [
                    (neighbor, 1)
                    for neighbor in neighbors
                ]

            result = self.ucs_search(
                weighted_graph,
                current_pos,
                goal_pos
            )

            if result:

                path, cost = result

        # A*
        elif self.active_algo == 'AStar':

            path = self.astar_search(
                current_pos,
                goal_pos,
                walls,
                grid_size,
                heuristic_type='manhattan'
            )

        # Convert path into movement actions
        if path and len(path) > 1:

            actions = []

            for current, next_pos in zip(
                path[:-1],
                path[1:]
            ):

                cx, cy = current
                nx, ny = next_pos

                if nx == cx and ny == cy + 1:
                    actions.append('Up')

                elif nx == cx and ny == cy - 1:
                    actions.append('Down')

                elif nx == cx - 1 and ny == cy:
                    actions.append('Left')

                elif nx == cx + 1 and ny == cy:
                    actions.append('Right')

            self.plan = actions

            if self.plan:
                return self.plan.pop(0)

        # Fallback movement
        return random.choice(
            ['Up', 'Down', 'Left', 'Right']
        )

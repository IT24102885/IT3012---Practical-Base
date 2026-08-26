# agent.py

import random
from collections import deque
import heapq

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
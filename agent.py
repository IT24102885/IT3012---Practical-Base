# agent.py

import random
from collections import deque
import heapq
import math

# ==========================================================
# Practical 04 - Logic Engine
# ==========================================================

from logic_engine import KnowledgeBase


class GreedyGridAgent:
    """
    A simple agent that tries to move around systematically
    to clear the grid.
    """

    def __init__(self):
        self.actions_pool = [
            'Up',
            'Down',
            'Left',
            'Right'
        ]

    def sense_and_act(self, percept: dict) -> str:

        pos = percept['agent_pos']

        return random.choice(
            self.actions_pool
        )


class SearchAgent:

    # ==========================================================
    # Practical 04 - Task 1.3
    # Initialize Search Agent and Knowledge Base
    # ==========================================================

    def __init__(self):

        # Default algorithm
        self.active_algo = 'AStar'

        # Store current movement plan
        self.plan = []

        # ======================================================
        # Practical 04 - Part 1
        # Create Knowledge Base
        # ======================================================

        self.kb = KnowledgeBase()

        # ======================================================
        # Practical 04 - Step 3.1
        # Define safety rules
        # ======================================================

        # Rule 1:
        # TargetVisible AND HasDust -> SafeToEngage
        self.kb.tell_rule(
            ['TargetVisible', 'HasDust'],
            'SafeToEngage'
        )

        # Rule 2:
        # SafeToEngage AND BloodseekerMissing -> Retreat
        self.kb.tell_rule(
            ['SafeToEngage', 'BloodseekerMissing'],
            'Retreat'
        )

    # ==========================================================
    # TASK 3 - BFS
    # ==========================================================

    def bfs_search(self, graph, start, goal):

        queue = deque(
            [(start, [start])]
        )

        # Task 6 - visited states
        reached = {start}

        while queue:

            current, path = queue.popleft()

            if current == goal:
                return path

            for neighbor in graph.get(
                current,
                []
            ):

                if neighbor not in reached:

                    reached.add(neighbor)

                    queue.append(
                        (
                            neighbor,
                            path + [neighbor]
                        )
                    )

        return None

    # ==========================================================
    # TASK 4 - DFS
    # ==========================================================

    def dfs_search(self, graph, start, goal):

        stack = [
            (start, [start])
        ]

        # Task 6 - visited states
        reached = {start}

        while stack:

            current, path = stack.pop()

            if current == goal:
                return path

            for neighbor in graph.get(
                current,
                []
            ):

                if neighbor not in reached:

                    reached.add(neighbor)

                    stack.append(
                        (
                            neighbor,
                            path + [neighbor]
                        )
                    )

        return None

    # ==========================================================
    # TASK 5 - UCS
    # ==========================================================

    def ucs_search(self, graph, start, goal):

        priority_queue = [
            (0, start, [start])
        ]

        # Task 6 - visited states
        reached = set()

        while priority_queue:

            cost, current, path = heapq.heappop(
                priority_queue
            )

            if current in reached:
                continue

            reached.add(current)

            if current == goal:
                return path, cost

            for neighbor, step_cost in graph.get(
                current,
                []
            ):

                if neighbor not in reached:

                    new_cost = cost + step_cost

                    heapq.heappush(
                        priority_queue,
                        (
                            new_cost,
                            neighbor,
                            path + [neighbor]
                        )
                    )

        return None

    # ==========================================================
    # Practical 04 - Task 1.1
    # Manhattan Distance Heuristic
    # ==========================================================

    def manhattan_distance(self, pos, goal):

        x1, y1 = pos
        x2, y2 = goal

        return (
            abs(x1 - x2)
            + abs(y1 - y2)
        )

    # ==========================================================
    # Practical 04 - Task 1.1
    # Euclidean Distance Heuristic
    # ==========================================================

    def euclidean_distance(self, pos, goal):

        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2
            + (y1 - y2) ** 2
        )

    # ==========================================================
    # Practical 04 - STEP 3.2
    # Check whether a tile is logically feasible
    # ==========================================================

    def is_tile_feasible(
        self,
        tile,
        food_positions,
        toxic_traps,
        opponents
    ):

        # ------------------------------------------------------
        # Clear old facts before checking a new tile
        # ------------------------------------------------------

        self.kb.clear_facts()

        # ------------------------------------------------------
        # Feed percepts of the candidate tile into KB
        # ------------------------------------------------------

        # TargetVisible:
        # Candidate tile contains food
        if tile in food_positions:

            self.kb.tell_fact(
                'TargetVisible'
            )

        # HasDust:
        # Candidate tile contains a toxic trap
        if tile in toxic_traps:

            self.kb.tell_fact(
                'HasDust'
            )

        # BloodseekerMissing:
        # No opponent is present on the candidate tile
        if tile not in opponents:

            self.kb.tell_fact(
                'BloodseekerMissing'
            )

        # ------------------------------------------------------
        # Run Forward Chaining
        # ------------------------------------------------------

        self.kb.forward_chain()

        # ------------------------------------------------------
        # If Retreat is deduced,
        # the tile is logically infeasible
        # ------------------------------------------------------

        if 'Retreat' in self.kb.facts:

            return False

        return True

    # ==========================================================
    # Practical 04 - Task 1.2 + Step 3.2
    # A* Search with Knowledge Base feasibility checking
    # ==========================================================

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        food_positions=None,
        toxic_traps=None,
        opponents=None,
        heuristic_type='manhattan'
    ):

        # ------------------------------------------------------
        # Default empty sets
        # ------------------------------------------------------

        if food_positions is None:
            food_positions = set()

        if toxic_traps is None:
            toxic_traps = set()

        if opponents is None:
            opponents = set()

        # ------------------------------------------------------
        # Priority Queue
        # ------------------------------------------------------

        priority_queue = []

        reached_states = set()

        # Select heuristic
        if heuristic_type == 'euclidean':

            heuristic = self.euclidean_distance

        else:

            heuristic = self.manhattan_distance

        # Initial costs
        g_cost = 0

        h_cost = heuristic(
            start_pos,
            goal_pos
        )

        f_cost = g_cost + h_cost

        heapq.heappush(
            priority_queue,
            (
                f_cost,
                g_cost,
                start_pos,
                [start_pos]
            )
        )

        width, height = grid_size

        # ------------------------------------------------------
        # A* Main Loop
        # ------------------------------------------------------

        while priority_queue:

            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(
                priority_queue
            )

            if current_pos in reached_states:
                continue

            if current_pos == goal_pos:
                return path_taken

            reached_states.add(
                current_pos
            )

            x, y = current_pos

            # --------------------------------------------------
            # Generate neighbouring nodes
            # --------------------------------------------------

            neighbors = [
                (x, y + 1),
                (x, y - 1),
                (x - 1, y),
                (x + 1, y)
            ]

            for neighbor in neighbors:

                nx, ny = neighbor

                # ----------------------------------------------
                # Check physical grid boundaries
                # ----------------------------------------------

                if nx < 0 or nx >= width:
                    continue

                if ny < 0 or ny >= height:
                    continue

                # ----------------------------------------------
                # Reachability Check
                # Physical wall
                # ----------------------------------------------

                if neighbor in walls:
                    continue

                if neighbor in reached_states:
                    continue

                # ==================================================
                # Practical 04 - STEP 3.2
                # KNOWLEDGE BASE FEASIBILITY CHECK
                # ==================================================

                tile_feasible = self.is_tile_feasible(
                    neighbor,
                    food_positions,
                    toxic_traps,
                    opponents
                )

                # --------------------------------------------------
                # If KB derives Retreat:
                # tile is logically INFEASIBLE
                # --------------------------------------------------

                if not tile_feasible:
                    continue

                # ----------------------------------------------
                # Calculate A* costs
                # ----------------------------------------------

                new_g = g_cost + 1

                new_h = heuristic(
                    neighbor,
                    goal_pos
                )

                new_f = new_g + new_h

                # ----------------------------------------------
                # Add feasible node to open list
                # ----------------------------------------------

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

    # ==========================================================
    # Practical 04 - Task 1.3
    # Integrate BFS, DFS, UCS and A*
    # ==========================================================

    def sense_and_act(
        self,
        percept: dict
    ):

        # ------------------------------------------------------
        # Continue existing movement plan
        # ------------------------------------------------------

        if self.plan:

            return self.plan.pop(0)

        # ------------------------------------------------------
        # Current position
        # ------------------------------------------------------

        current_pos = tuple(
            percept['agent_pos']
        )

        # ------------------------------------------------------
        # Get walls
        # ------------------------------------------------------

        walls = set(
            tuple(wall)
            for wall in percept['walls']
        )

        # ------------------------------------------------------
        # Grid size
        # ------------------------------------------------------

        grid_size = percept['grid_size']

        # ------------------------------------------------------
        # Remaining food
        # ------------------------------------------------------

        remaining_food = [
            tuple(food)
            for food in percept['all_food']
        ]

        # ------------------------------------------------------
        # Toxic traps
        # ------------------------------------------------------

        toxic_traps = set(
            tuple(trap)
            for trap in percept.get(
                'toxic_traps',
                []
            )
        )

        # ------------------------------------------------------
        # Opponents
        # ------------------------------------------------------

        opponents = set(
            tuple(opponent)
            for opponent in percept.get(
                'opponents',
                []
            )
        )

        # ------------------------------------------------------
        # No food remaining
        # ------------------------------------------------------

        if not remaining_food:

            return random.choice(
                [
                    'Up',
                    'Down',
                    'Left',
                    'Right'
                ]
            )

        # ------------------------------------------------------
        # Find closest food
        # ------------------------------------------------------

        goal_pos = min(
            remaining_food,
            key=lambda food:
                self.manhattan_distance(
                    current_pos,
                    food
                )
        )

        width, height = grid_size

        # ======================================================
        # Create Grid Graph
        # ======================================================

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
                        and 0 <= ny < height
                        and neighbor not in walls
                    ):

                        valid_neighbors.append(
                            neighbor
                        )

                graph[current] = valid_neighbors

        # ======================================================
        # Search Path
        # ======================================================

        path = None

        # ------------------------------------------------------
        # BFS
        # ------------------------------------------------------

        if self.active_algo == 'BFS':

            path = self.bfs_search(
                graph,
                current_pos,
                goal_pos
            )

        # ------------------------------------------------------
        # DFS
        # ------------------------------------------------------

        elif self.active_algo == 'DFS':

            path = self.dfs_search(
                graph,
                current_pos,
                goal_pos
            )

        # ------------------------------------------------------
        # UCS
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # A*
        # ------------------------------------------------------

        elif self.active_algo == 'AStar':

            path = self.astar_search(
                current_pos,
                goal_pos,
                walls,
                grid_size,
                food_positions=set(
                    remaining_food
                ),
                toxic_traps=toxic_traps,
                opponents=opponents,
                heuristic_type='manhattan'
            )

        # ======================================================
        # Convert path to actions
        # ======================================================

        if path and len(path) > 1:

            actions = []

            for current, next_pos in zip(
                path[:-1],
                path[1:]
            ):

                cx, cy = current
                nx, ny = next_pos

                if (
                    nx == cx
                    and ny == cy + 1
                ):

                    actions.append(
                        'Up'
                    )

                elif (
                    nx == cx
                    and ny == cy - 1
                ):

                    actions.append(
                        'Down'
                    )

                elif (
                    nx == cx - 1
                    and ny == cy
                ):

                    actions.append(
                        'Left'
                    )

                elif (
                    nx == cx + 1
                    and ny == cy
                ):

                    actions.append(
                        'Right'
                    )

            self.plan = actions

            if self.plan:

                return self.plan.pop(0)

        # ======================================================
        # Fallback Movement
        # ======================================================

        return random.choice(
            [
                'Up',
                'Down',
                'Left',
                'Right'
            ]
        )
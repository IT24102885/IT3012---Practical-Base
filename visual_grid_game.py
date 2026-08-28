# visual_grid_game.py

import random
import tkinter as tk
from agent import SearchAgent


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):

        self.width = width
        self.height = height

        self.agent_pos = [0, 0]

        if custom_walls is not None:

            self.walls = set(
                custom_walls
            )

        else:

            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # ==========================================================
        # FOOD
        # ==========================================================

        self.food_positions = set()

        while len(
            self.food_positions
        ) < num_food:

            fx = random.randint(
                0,
                self.width - 1
            )

            fy = random.randint(
                0,
                self.height - 1
            )

            pos_tuple = (
                fx,
                fy
            )

            if (
                pos_tuple != (0, 0)
                and pos_tuple not in self.walls
            ):

                self.food_positions.add(
                    pos_tuple
                )

        # ==========================================================
        # TOXIC TRAPS
        # Original brown block generation kept unchanged
        # ==========================================================

        self.toxic_traps = set()

        num_traps = 5

        while len(
            self.toxic_traps
        ) < num_traps:

            tx = random.randint(
                0,
                self.width - 1
            )

            ty = random.randint(
                0,
                self.height - 1
            )

            trap_pos = (
                tx,
                ty
            )

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):

                self.toxic_traps.add(
                    trap_pos
                )

        # ==========================================================
        # OPPONENTS
        # ==========================================================

        self.opponents = []

        while len(
            self.opponents
        ) < num_opponents:

            ox = random.randint(
                0,
                self.width - 1
            )

            oy = random.randint(
                0,
                self.height - 1
            )

            op_pos = [
                ox,
                oy
            ]

            if (
                tuple(op_pos) != (0, 0)
                and tuple(op_pos) not in self.walls
                and tuple(op_pos) not in self.food_positions
            ):

                self.opponents.append(
                    op_pos
                )

        self.score = 0
        self.steps = 0
        self.collision = False

    # ==========================================================
    # PERCEPT
    # ==========================================================

    def get_percept(self) -> dict:

        x, y = self.agent_pos

        front_x = x
        front_y = y + 1

        wall_ahead = (
            front_y >= self.height
            or (
                front_x,
                front_y
            ) in self.walls
        )

        food_here = (
            x,
            y
        ) in self.food_positions

        # Practical 04 - Task 1.3
        return {

            "agent_pos":
                tuple(self.agent_pos),

            "wall_ahead":
                wall_ahead,

            "food_here":
                food_here,

            "grid_size":
                (
                    self.width,
                    self.height
                ),

            "walls":
                list(self.walls),

            "all_food":
                list(self.food_positions),

            # ==================================================
            # Practical 04 - Logic Engine percepts
            # ==================================================

            "toxic_traps":
                list(self.toxic_traps),

            "opponents":
                list(self.opponents)
        }

    # ==========================================================
    # EXECUTE ACTION
    # ==========================================================

    def execute_action(
        self,
        action: str
    ):

        self.steps += 1

        new_pos = list(
            self.agent_pos
        )

        if action == "Up":

            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == "Down":

            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == "Left":

            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == "Right":

            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )

        # ==========================================================
        # WALL COLLISION
        # ==========================================================

        if tuple(new_pos) in self.walls:

            self.score -= 5

        else:

            self.agent_pos = new_pos

        tuple_pos = tuple(
            self.agent_pos
        )

        # ==========================================================
        # FOOD
        # ==========================================================

        if tuple_pos in self.food_positions:

            self.food_positions.remove(
                tuple_pos
            )

            self.score += 20

        # ==========================================================
        # CHECK TOXIC TRAP
        # Original brown block logic kept unchanged
        # ==========================================================

        if tuple_pos in self.toxic_traps:

            self.score -= 15

        # ==========================================================
        # MOVE OPPONENTS
        # ==========================================================

        for op in self.opponents:

            move = random.choice(
                [
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "Stay"
                ]
            )

            if (
                move == "Up"
                and op[1] < self.height - 1
            ):

                op[1] += 1

            elif (
                move == "Down"
                and op[1] > 0
            ):

                op[1] -= 1

            elif (
                move == "Left"
                and op[0] > 0
            ):

                op[0] -= 1

            elif (
                move == "Right"
                and op[0] < self.width - 1
            ):

                op[0] += 1

            # Check collision
            if op == self.agent_pos:

                self.score -= 50

                self.collision = True

    # ==========================================================
    # GAME END
    # ==========================================================

    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Scalable Multi-Agent Grid Hunt"
        )

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # Practical 04 - Task 1.3
        self.agent = SearchAgent()

        # ==========================================================
        # DEFAULT SEARCH ALGORITHM
        # ==========================================================

        self.agent.active_algo = "AStar"

        # ==========================================================
        # CELL SIZE
        # ==========================================================

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_w = (
            self.env.width
            * self.cell_size
        )

        canvas_h = (
            self.env.height
            * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )

        self.canvas.pack()

        # ==========================================================
        # STATUS LABEL
        # ==========================================================

        self.label = tk.Label(
            root,
            text="Algorithm: AStar | Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=10
        )

        # ==========================================================
        # ALGORITHM SELECTION
        # ==========================================================

        algorithm_frame = tk.Frame(
            root
        )

        algorithm_frame.pack(
            pady=5
        )

        tk.Button(
            algorithm_frame,
            text="BFS",
            command=lambda:
                self.set_algorithm("BFS"),
            font=("Arial", 10)
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        tk.Button(
            algorithm_frame,
            text="DFS",
            command=lambda:
                self.set_algorithm("DFS"),
            font=("Arial", 10)
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        tk.Button(
            algorithm_frame,
            text="UCS",
            command=lambda:
                self.set_algorithm("UCS"),
            font=("Arial", 10)
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        tk.Button(
            algorithm_frame,
            text="A*",
            command=lambda:
                self.set_algorithm("AStar"),
            font=("Arial", 10)
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        # ==========================================================
        # START SIMULATION
        # ==========================================================

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(
            pady=5
        )

        self.draw_grid()

    # ==========================================================
    # SET SELECTED ALGORITHM
    # ==========================================================

    def set_algorithm(
        self,
        algorithm
    ):

        # Store selected algorithm
        self.agent.active_algo = algorithm

        # Clear previous search plan
        self.agent.plan = []

        self.label.config(
            text=(
                f"Algorithm: {algorithm} | "
                f"Score: {self.env.score} | "
                f"Steps: {self.env.steps}"
            )
        )

    # ==========================================================
    # DRAW GRID
    # ==========================================================

    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        # ==========================================================
        # DRAW CELLS
        # ==========================================================

        for x in range(
            self.env.width
        ):

            for y in range(
                self.env.height
            ):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                color = (
                    "#f1f5f9"
                    if (
                        x,
                        y
                    ) not in self.env.walls
                    else "#64748b"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                if (
                    self.cell_size >= 40
                    and (
                        x,
                        y
                    ) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1
                        + self.cell_size / 2,
                        y1
                        + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=(
                            "Arial",
                            8,
                            "bold"
                        )
                    )

        # ==========================================================
        # DRAW FOOD
        # ==========================================================

        for fx, fy in self.env.food_positions:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                fx
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - fy
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1
                + self.cell_size * 0.5,
                y1
                + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # ==========================================================
        # DRAW OPPONENTS
        # ==========================================================

        for ox, oy in self.env.opponents:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                ox
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - oy
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1
                + self.cell_size * 0.6,
                y1
                + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # ==========================================================
        # DRAW TOXIC TRAPS
        # Brown block remains in the same place/logic
        # ==========================================================

        for tx, ty in self.env.toxic_traps:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                tx
                * self.cell_size
                + offset
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - ty
                )
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1
                + self.cell_size * 0.5,
                y1
                + self.cell_size * 0.5,
                fill="#7c2d12",
                outline="#451a03"
            )

        # ==========================================================
        # DRAW AGENT
        # ==========================================================

        ax, ay = self.env.agent_pos

        offset = (
            self.cell_size
            * 0.15
        )

        x1 = (
            ax
            * self.cell_size
            + offset
        )

        y1 = (
            (
                self.env.height
                - 1
                - ay
            )
            * self.cell_size
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1
            + self.cell_size * 0.7,
            y1
            + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

    # ==========================================================
    # RUN SIMULATION
    # ==========================================================

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # ==================================================
                # GET CURRENT PERCEPT
                # ==================================================

                percept = (
                    self.env.get_percept()
                )

                # ==================================================
                # SEARCH AGENT
                #
                # The selected algorithm is stored in:
                # self.agent.active_algo
                #
                # A* additionally uses the Knowledge Base
                # to check logical feasibility.
                # ==================================================

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # ==================================================
                # EXECUTE ACTION
                # ==================================================

                self.env.execute_action(
                    action
                )

                # ==================================================
                # REDRAW GRID
                # ==================================================

                self.draw_grid()

                # ==================================================
                # SHOW SELECTED ALGORITHM
                # ==================================================

                self.label.config(
                    text=(
                        f"Algorithm: "
                        f"{self.agent.active_algo} | "
                        f"Score: "
                        f"{self.env.score} | "
                        f"Steps: "
                        f"{self.env.steps} | "
                        f"Action: "
                        f"{action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        f"Algorithm: "
                        f"{self.agent.active_algo} | "
                        f"Collision! Game Over! | "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                elif (
                    len(
                        self.env.food_positions
                    ) == 0
                ):

                    end_text = (
                        f"Algorithm: "
                        f"{self.agent.active_algo} | "
                        f"Finished! | "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    end_text = (
                        f"Algorithm: "
                        f"{self.agent.active_algo} | "
                        f"Time Up! | "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":

    root = tk.Tk()

    # 12x12 grid with 15 food and no opponents
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()
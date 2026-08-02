
class ModelBasedAgent:

    def __init__(self):
        # Internal memory
        self.visited_cells = set()
        self.last_action = None

    def sense_and_act(self, percept):
        # Update internal state (Sensor & Transition Model)
        current_state = (
            percept["wall_ahead"],
            percept["food_here"]
        )

        self.visited_cells.add(current_state)

        # IF food is here THEN suck
        if percept["food_here"]:
            self.last_action = "Suck"
            return "Suck"

        # IF wall ahead AND this situation was seen before THEN turn right
        if percept["wall_ahead"] and current_state in self.visited_cells:
            self.last_action = "Right"
            return "Right"

        # IF wall ahead THEN turn left
        if percept["wall_ahead"]:
            self.last_action = "Left"
            return "Left"

        # ELSE move forward
        self.last_action = "Up"
        return "Up"
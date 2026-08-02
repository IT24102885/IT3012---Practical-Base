

class SimpleReflexAgent:

    def sense_and_act(self, percept):

        # IF food is here THEN suck
        if percept["food_here"]:
            return "Suck"

        # IF wall ahead THEN turn left
        elif percept["wall_ahead"]:
            return "Left"

        # ELSE move forward
        else:
            return "Up"
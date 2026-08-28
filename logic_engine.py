# logic_engine.py

class KnowledgeBase:
    """
    Knowledge Base for storing facts and Horn Clause rules.
    """

    def __init__(self):
        # Store unique facts
        self.facts = set()

        # Store rules as:
        # (premise_list, conclusion)
        self.rules = []

    def tell_fact(self, fact_string):
        """
        Add a fact to the Knowledge Base.
        """
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """
        Add a rule to the Knowledge Base.
        """
        self.rules.append(
            (premise_list, conclusion_string)
        )

    def clear_facts(self):
        """
        Remove all current facts.
        Rules remain unchanged.
        """
        self.facts.clear()

    def forward_chain(self):
        """
        Data-driven Forward Chaining inference engine.

        Continues applying rules until no new facts
        can be deduced.
        """

        new_facts_added = True

        while new_facts_added:

            new_facts_added = False

            for premises, conclusion in self.rules:

                # Only derive conclusion if it is new
                if conclusion not in self.facts:

                    # Modus Ponens:
                    # All premises must already be facts
                    if all(
                        premise in self.facts
                        for premise in premises
                    ):
                        self.facts.add(conclusion)

                        new_facts_added = True
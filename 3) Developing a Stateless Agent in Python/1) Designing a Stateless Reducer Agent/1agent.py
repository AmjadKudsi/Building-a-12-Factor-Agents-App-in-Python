# TODO: Define the Agent class with the following:
#   - An __init__ method that accepts: model, reasoning_effort, extra_instructions, max_steps
#   - Store model, reasoning_effort, and max_steps as instance attributes
#   - Build self.system_prompt by concatenating a base prompt with extra_instructions


class Agent:
    def __init__(
        self,
        model="gpt-5",
        reasoning_effort="low",
        extra_instructions="",
        max_steps=10,
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps

        base_prompt = (
            "You are an autonomous agent capable of taking multiple tool-calling steps. "
            "When you are finished, call the final_answer tool. "
            "ALWAYS prefer tools for computations and transformations rather than fabricating results. "
        )

        self.system_prompt = base_prompt + extra_instructions
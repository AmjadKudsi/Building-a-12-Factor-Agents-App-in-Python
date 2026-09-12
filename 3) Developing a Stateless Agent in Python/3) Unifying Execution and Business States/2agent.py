import json
import openai
from pathlib import Path
from typing import List, Any
from core.models.state import State
from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
from core.utils.context_serializer import serialize_context_to_text


class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps

        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions

        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        serialized_content = serialize_context_to_text(context)
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=serialized_content,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    # TODO: Change this method to accept a State object instead of a context list,
    # and return the State object instead of a tuple.
    # At the start of the method, increment state.steps by 1.
    # Use state.context wherever the old code used the context list.
    # For final_answer, set state.status to "complete" and state.final_answer
    # to the answer value, then return the state.
    # At the end, return the state instead of a tuple.
    def _next_step(self, state: State) -> State:
        state.steps += 1

        response = self._call_llm(state.context)
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)

            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })

            if call_name == "final_answer":
                state.status = "complete"
                state.final_answer = call_arguments.get("answer")
                return state

            match call_name:
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})

                case _:
                    output = json.dumps({
                        "result": f"Error: Tool {call_name} not found"
                    })

            state.context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

        return state

    # TODO: Change this method to accept a State object and return a State object.
    # Create a deep copy using state = state.model_copy(deep=True) at the start.
    # Explicitly set state.error = None to clear any old errors.
    # Wrap the loop in a try/except block.
    # Inside the loop: check state.status and state.steps, then call _next_step.
    # In the except block: set state.status = "failed", state.error = str(e), and return state.
    # If the loop ends with state.status still "running", set it to "max_steps_reached".
    # Return the state object instead of a tuple.
    def run(self, state: State) -> State:
        state = state.model_copy(deep=True)
        state.error = None

        try:
            while state.status == "running" and state.steps < self.max_steps:
                state = self._next_step(state)

        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            return state

        if state.status == "running":
            state.status = "max_steps_reached"

        return state
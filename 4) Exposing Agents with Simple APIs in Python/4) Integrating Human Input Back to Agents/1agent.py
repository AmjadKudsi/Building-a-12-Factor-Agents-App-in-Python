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
        # TODO: Load the ask_human tool schema from ask_human.json
        with open(schemas_dir / "ask_human.json", "r", encoding="utf-8") as f:
            ask_human_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema,
            # TODO: Add ask_human_schema to the tool list
            ask_human_schema,
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

    def _next_step(self, state: State):
        state.steps += 1

        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]
            call_id = function_call["call_id"]

            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })

            match call_name:
                # TODO: Add a special ask_human case that removes the tool call,
                # sets state.status to "waiting_human_input", and returns state
                case "ask_human":
                    state.pending_tool_calls.remove(function_call)
                    state.status = "waiting_human_input"
                    return state
                case "final_answer":
                    state.pending_tool_calls = []
                    state.status = "complete"
                    state.final_answer = call_arguments.get("answer")
                    return state
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
                    output = json.dumps({"result": f"Error: Tool {call_name} not found"})

            state.pending_tool_calls.remove(function_call)
            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

        response = self._call_llm(state.context)
        function_calls = [item for item in response.output if item.type == "function_call"]

        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),
                "call_id": fc.call_id,
                "type": fc.type
            }
            for fc in function_calls
        ]

        state.pending_tool_calls.extend(function_call_dicts)
        return state

    def run(self, state: State, progress_callback=None):
        """
        Execute agent steps on a given state and persist progress.
        """
        state = state.model_copy(deep=True)

        # Ensure state is set to running
        state.status = "running"
        state.error = None
        
        # Calculate max steps: if resuming (steps > 0), allow continuing from current step count
        is_resuming = state.steps > 0
        max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps

        try:
            # Call next step until complete or waiting_human_input
            while state.status == "running" and state.steps < max_steps_allowed:
                state = self._next_step(state)
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(state)

            # If still running and max steps reached, set status to max_steps_reached
            if state.status == "running" and state.steps >= max_steps_allowed:
                state.status = "max_steps_reached"
            
            return state
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            state.pending_tool_calls = []
            if progress_callback:
                progress_callback(state)
            return state
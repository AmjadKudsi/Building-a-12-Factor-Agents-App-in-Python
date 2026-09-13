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

    def _next_step(self, state: State):
        state.steps += 1

        # TODO: Before calling the LLM, add a loop that processes pending tool calls
        # from the PREVIOUS step. Iterate over list(state.pending_tool_calls) and
        # for each call dict:
        #   1. Extract call_name, call_arguments, and call_id from the dict.
        #   2. Append a function_call entry to state.context with keys: type, name,
        #      arguments (use json.dumps on call_arguments), and call_id.
        #   3. Use a match/case block on call_name:
        #      - "final_answer": clear state.pending_tool_calls to [], set
        #        state.status to "complete", set state.final_answer from
        #        call_arguments.get("answer"), and return state immediately.
        #      - For each math tool (sum_numbers, multiply_numbers, etc.): execute
        #        in a try/except and build an output JSON string.
        #      - Default case: build an error output for unknown tools.
        #   4. After executing, remove the call from state.pending_tool_calls and
        #      append a function_call_output entry to state.context with the output.

        for call in list(state.pending_tool_calls):
            call_name = call["name"]
            call_arguments = call["arguments"]
            call_id = call["call_id"]

            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })

            if call_name == "final_answer":
                state.pending_tool_calls = []
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

            state.pending_tool_calls.remove(call)

            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

        # TODO: Replace the code below so it only queues new calls instead of
        # executing them. Keep the _call_llm call, but change the for loop to:
        #   1. Convert each function_call from the response into a dict with keys:
        #      name, arguments (parsed from JSON), call_id, and type.
        #   2. Collect all dicts into a list and extend state.pending_tool_calls.
        #   3. Return state without executing any of the new calls.
        response = self._call_llm(state.context)
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        new_pending_calls = []

        for fc in function_calls:
            new_pending_calls.append({
                "name": fc.name,
                "arguments": json.loads(fc.arguments),
                "call_id": fc.call_id,
                "type": fc.type
            })

        state.pending_tool_calls.extend(new_pending_calls)

        return state
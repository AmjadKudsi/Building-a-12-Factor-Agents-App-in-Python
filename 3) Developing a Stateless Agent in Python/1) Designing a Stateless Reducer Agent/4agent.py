import json
import openai
from pathlib import Path
from typing import List, Any


class Agent:
    """
    A stateless reducer agent that processes context step-by-step.
    
    This exercise focuses on implementing the first half of _next_step:
    parsing model responses and handling the completion signal.
    Tool execution will be added in a future exercise.
    """
    
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        """
        Initialize the Agent with configuration parameters and load tool schemas.
        
        Args:
            model: The model to use for generation (default: "gpt-5")
            reasoning_effort: The reasoning effort level for gpt-5 (default: "low")
            extra_instructions: Additional instructions to append to the system prompt
            max_steps: Maximum number of steps the agent can take (default: 10)
        """
        # Store model configuration
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        
        # Build the system prompt by combining base prompt with extra instructions
        self.system_prompt = (
            "You are an autonomous agent that can take multiple tool-calling steps. "
            "If your work is done, call the final_answer tool. "
            "ALWAYS prefer calling tools to compute, fetch, or transform information "
            "rather than fabricating results."
        ) + extra_instructions
        
        # Load tool schemas from JSON files
        # Using Path makes this portable across different environments
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)
        
        # Combine all schemas into a single list
        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]
    
    def _call_llm(self, context: List[Any]):
        """
        Call the LLM with the current context.
        Returns the model's response, which will include tool calls.
        
        Args:
            context: The full conversation history
            
        Returns:
            The model's response object
        """
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response
    
    def _next_step(self, context: List[Any]):
        """
        Execute one step of the agent loop:
        1. Call the LLM
        2. Extract function calls from the response
        3. Record function calls in context
        4. Check for completion signal (final_answer)
        
        Note: This exercise focuses on parsing and completion detection.
        Tool execution will be added in a future exercise.
        
        Returns: (updated_context, status, final_answer)
            - updated_context: The context list with new function calls appended
            - status: "complete" if final_answer was called, "running" otherwise
            - final_answer: The answer string if complete, None otherwise
        """
        # TODO: Call self._call_llm(context) and store the result in a variable called response
        response = self._call_llm(context)
        
        # TODO: Extract all items from response.output where item.type == "function_call" into a list called function_calls
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]
        
        # TODO: Loop through each function call (fc) in function_calls:
        for fc in function_calls:
        
            # TODO: Get the function name from fc.name and store it in call_name
            call_name = fc.name
            
            # TODO: Parse fc.arguments using json.loads() and store it in call_arguments
            call_arguments = json.loads(fc.arguments)
            
            # TODO: Append a dictionary to context with:
            #   - "type": "function_call"
            #   - "name": call_name
            #   - "arguments": fc.arguments (use the original string, not call_arguments)
            #   - "call_id": fc.call_id
            context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })
            
            # TODO: Check if call_name equals "final_answer"
            # If it does, return a tuple: (context, "complete", call_arguments.get("answer"))
            if call_name == "final_answer":
                return (context, "complete", call_arguments.get("answer"))
        
        # TODO: After processing all function calls, return (context, "running", None)
        return (context, "running", None)
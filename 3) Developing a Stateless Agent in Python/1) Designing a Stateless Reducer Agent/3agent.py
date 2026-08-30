import json
import openai
from pathlib import Path
from typing import List, Any


class Agent:
    """
    A stateless reducer agent that processes context step-by-step.
    
    This exercise focuses on implementing the _call_llm method to interface with the model API.
    The reducer logic (_next_step and run) will be added in future exercises.
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
        # TODO: Call openai.responses.create with the following parameters:
        #   - model=self.model
        #   - instructions=self.system_prompt
        #   - input=context
        #   - tools=self.tool_schemas
        #   - tool_choice="required"
        #   - reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        
        # TODO: Return the response object
        
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response
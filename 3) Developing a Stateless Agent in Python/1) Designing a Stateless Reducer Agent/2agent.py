import json
from pathlib import Path


class Agent:
    """
    A stateless reducer agent that processes context step-by-step.
    
    This exercise focuses on loading tool schemas from external JSON files.
    The agent's execution logic (_call_llm, _next_step, run) will be added in future exercises.
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
        
        # TODO: Compute the schemas_dir path relative to this file
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        
        # TODO: Open and load math.json (UTF-8) into math_schemas (this will be a list)
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        
        # TODO: Open and load final_answer.json (UTF-8) into final_answer_schema (this will be a dict)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)
        
        # TODO: Combine all schemas into self.tool_schemas as a single list (all math schemas, then final_answer_schema)
        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]
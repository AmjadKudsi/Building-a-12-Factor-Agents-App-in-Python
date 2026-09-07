import json
from typing import List, Dict, Any
from pathlib import Path


_template_path = Path(__file__).resolve().parent.parent / "prompts" / "context_format.md"
_CONTEXT_TEMPLATE = _template_path.read_text(encoding="utf-8")


def serialize_context_to_text(context: List[Dict[str, Any]]) -> str:
    """
    Transform the raw context list into structured markdown text.
    Returns a formatted string ready to send to the model.
    """
    if not context:
        return ""

    user_message = ""
    for item in context:
        if item.get("role") == "user":
            user_message = item.get("content", "")
            break

    # TODO: Build call_map by iterating through context items with type "function_call"
    # For each function_call, extract call_id, name, and arguments
    # If arguments is a JSON string, parse it to a dict using json.loads
    # Format dict arguments as "k=repr(v)" pairs joined by ", "
    # Store the formatted signature as "function_name(args)" in call_map[call_id]
    call_map = {}

    for item in context:
        if item.get("type") == "function_call":
            call_id = item.get("call_id")
            name = item.get("name", "unknown_function")
            arguments = item.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            if isinstance(arguments, dict):
                formatted_args = ", ".join(
                    f"{key}={repr(value)}"
                    for key, value in arguments.items()
                )
            else:
                formatted_args = repr(arguments)

            if call_id:
                call_map[call_id] = f"{name}({formatted_args})"

    # TODO: Build execution history lines by iterating through context items with type "function_call_output"
    # For each output, extract call_id and output value
    # Look up the formatted call signature in call_map (use unknown_call(call_id) as fallback)
    # Append a line like "✓ COMPLETED: <signature> → Result: <output>"
    history_lines = []

    for item in context:
        if item.get("type") == "function_call_output":
            call_id = item.get("call_id")
            output = item.get("output", "")

            signature = call_map.get(
                call_id,
                f"unknown_call({call_id})"
            )

            history_lines.append(
                f"✓ COMPLETED: {signature} → Result: {output}"
            )

    # TODO: Join the lines into a single string or use the default message if empty
    execution_history = (
        "\n".join(history_lines)
        if history_lines
        else "(No actions completed yet)"
    )

    return _CONTEXT_TEMPLATE.format(
        user_message=user_message,
        execution_history=execution_history
    )
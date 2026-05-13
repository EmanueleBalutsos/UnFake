from typing import Any

_UNSUPPORTED_KEYS = {"title", "additionalProperties", "maxItems", "minItems", "$schema"}


def resolve_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Inline all $ref/$defs in a Pydantic-generated JSON Schema and strip keys
    that Gemini's response_schema does not support.
    """
    defs = schema.get("$defs", {})
    resolved = _resolve_node(schema, defs)
    resolved.pop("$defs", None)
    return resolved


def _resolve_node(node: Any, defs: dict[str, Any]) -> Any:
    if not isinstance(node, dict):
        return node

    if "$ref" in node:
        ref_path = node["$ref"]  # e.g. "#/$defs/AgencyModel"
        ref_name = ref_path.split("/")[-1]
        return _resolve_node(defs[ref_name], defs)

    return {
        k: _resolve_node(v, defs)
        for k, v in node.items()
        if k not in _UNSUPPORTED_KEYS
    }

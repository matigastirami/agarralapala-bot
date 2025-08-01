from langchain_core.tools import tool

@tool(return_direct=True)
def return_as_json(data: str) -> dict:
    """
    Takes a description or structured list and converts it into valid JSON.
    """
    import json
    try:
        return json.loads(data)
    except Exception:
        return {"error": "Invalid JSON, here is the raw data", "raw": data}

@tool()
def convert_to_json(data: str) -> dict:
    """
    Takes a description or structured list and converts it into valid JSON.
    """
    import json
    try:
        return json.loads(data)
    except Exception:
        return {"error": "Invalid JSON, here is the raw data", "raw": data}
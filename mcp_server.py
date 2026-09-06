"""
MCP Server for Temporal Plan Simple Temporal Network STN Skill.
"""

import json
import sys
from client import SimpleTemporalNetwork

STN = SimpleTemporalNetwork()


def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "add_temporal_constraint",
                    "description": "Add interval constraint between two timepoints: target - source in [min, max]",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "min_duration": {"type": "number"},
                            "max_duration": {"type": "number"}
                        },
                        "required": ["source", "target", "min_duration", "max_duration"]
                    }
                },
                {
                    "name": "solve_stn",
                    "description": "Check temporal consistency and compute earliest/latest bounds",
                    "inputSchema": {
                        "type": "object"
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "add_temporal_constraint":
            STN.add_constraint(
                args["source"],
                args["target"],
                args["min_duration"],
                args["max_duration"]
            )
            return {"content": [{"type": "text", "text": json.dumps({"status": "constraint_added"})}]}

        elif tool_name == "solve_stn":
            res = STN.solve()
            return {"content": [{"type": "text", "text": json.dumps(res)}]}

        return {"error": f"Unknown tool: {tool_name}"}

    return {"error": f"Unknown method: {method}"}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            resp["id"] = req.get("id")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

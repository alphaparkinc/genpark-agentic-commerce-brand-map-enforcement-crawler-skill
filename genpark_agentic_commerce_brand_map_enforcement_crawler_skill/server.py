# -*- coding: utf-8 -*-
"""MCP Server for Brand Minimum Advertised Price (MAP) Automated Compliance Sentinel Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import BrandMAPEnforcementCrawlerSentinel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "audit_reseller_map_violations",
        "description": "Detect listings selling below contracted MAP floor price and quantify brand price erosion margin.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_sku": {
                    "type": "string"
                },
                "map_floor_price_usd": {
                    "type": "number"
                },
                "observed_listings": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            },
            "required": [
                "product_sku",
                "map_floor_price_usd",
                "observed_listings"
            ]
        }
    },
    {
        "name": "generate_automated_cease_and_desist_map_notice",
        "description": "Draft automated MAP violation notice with timestamped evidence and cure window for unauthorized distributor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "merchant_name": {
                    "type": "string"
                },
                "sku": {
                    "type": "string"
                },
                "violation_price_usd": {
                    "type": "number"
                },
                "map_floor_usd": {
                    "type": "number"
                },
                "marketplace": {
                    "type": "string"
                }
            },
            "required": [
                "merchant_name",
                "sku",
                "violation_price_usd",
                "map_floor_usd"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-brand-map-enforcement-crawler-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(BrandMAPEnforcementCrawlerSentinel, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-agentic-commerce-brand-map-enforcement-crawler-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()

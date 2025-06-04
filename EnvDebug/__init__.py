# EnvDebug/__init__.py

import os
import json
import logging
import azure.functions as func
from . import test_alerts

def main(req: func.HttpRequest) -> func.HttpResponse:
    mode = req.params.get("mode", "test")

    if mode == "env":
        env_vars = {
            key: value for key, value in os.environ.items()
            if "DISCORD" in key or "KEYVAULT" in key or "WEBHOOK" in key
        }
        return func.HttpResponse(
            json.dumps(env_vars, indent=2),
            mimetype="application/json",
            status_code=200
        )

    elif mode == "test":
        logging.info("🔧 Running on-demand alert + logging test")
        try:
            test_alerts.main()
            return func.HttpResponse("✅ Test alerts sent and logged.", status_code=200)
        except Exception as e:
            logging.exception("❌ test_alerts.main() failed")
            return func.HttpResponse(f"❌ Error: {str(e)}", status_code=500)

    return func.HttpResponse("❌ Invalid mode. Use ?mode=test or ?mode=env", status_code=400)

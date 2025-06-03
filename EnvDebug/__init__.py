import os
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    env_vars = {key: value for key, value in os.environ.items() if "DISCORD" in key or "KEYVAULT" in key or "WEBHOOK" in key}
    
    return func.HttpResponse(
        json.dumps(env_vars, indent=2),
        mimetype="application/json",
        status_code=200
    )

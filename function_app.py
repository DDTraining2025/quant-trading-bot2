import azure.functions as func

# 1) Load secrets at startup
from keyvaultloader import load_secrets_from_vault
load_secrets_from_vault()

# 2) Import only your Function blueprints
from azfuncs.intraday_alert import bp as intraday_bp
from azfuncs.rss_listener    import bp as rss_bp
from azfuncs.outcome_tracker import bp as outcome_bp

# 3) Wire them into the FunctionApp
app = func.FunctionApp()
app.register_functions(intraday_bp)
app.register_functions(rss_bp)
app.register_functions(outcome_bp)

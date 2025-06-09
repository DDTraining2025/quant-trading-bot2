import azure.functions as func
from azure.functions import FunctionApp, TimerRequest

# load secrets once at startup
from keyvaultloader import load_secrets_from_vault
load_secrets_from_vault()

# import your three blueprints
from azfuncs.intraday_alert import bp as intraday_bp
from azfuncs.rss_listener    import bp as rss_bp
from azfuncs.outcome_tracker import bp as outcome_bp

app = FunctionApp()

# register the blueprints you defined in azfuncs/*
app.register_functions(intraday_bp)
app.register_functions(rss_bp)
app.register_functions(outcome_bp)

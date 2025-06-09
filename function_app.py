# function_app.py
import logging
import azure.functions as func

# 1) load secrets once at startup
from keyvaultloader import load_secrets_from_vault
load_secrets_from_vault()

# 2) import your blueprints
from azfuncs.intraday_alert import bp as intraday_bp
from azfuncs.rss_listener    import bp as rss_bp
from azfuncs.outcome_tracker import bp as outcome_bp
from azfuncs.hello_timer      import bp as hello_bp

# 3) wire them into a single FunctionApp
logging.basicConfig(level=logging.INFO)
app = func.FunctionApp()

app.register_functions(intraday_bp)
logging.info("🔌 Registered IntradayAlert blueprint")

app.register_functions(rss_bp)
logging.info("🔌 Registered RSSListener blueprint")

app.register_functions(outcome_bp)
logging.info("🔌 Registered OutcomeTracker blueprint")

app.register_functions(hello_bp)

# function_app.py
import azure.functions as func
from IntradayAlert import bp as intraday_bp
from OutcomeTracker import bp as outcome_bp
from dbwriter import bp as dbwriter_bp
from discordposter import bp as discord_bp
from entrytarget import bp as entrytarget_bp
from finnhubapi import bp as finnhub_bp
from keyvaultloader import bp as keyvault_bp
from logger import bp as logger_bp
from mcpscore import bp as mcpscore_bp
from nlpprocessor import bp as nlpproc_bp
from rsslistener import bp as rsslistener_bp

app = func.FunctionApp()

# Register Blueprints (modules)
app.register_functions(intraday_bp)
app.register_functions(outcome_bp)
app.register_functions(dbwriter_bp)
app.register_functions(discord_bp)
app.register_functions(entrytarget_bp)
app.register_functions(finnhub_bp)
app.register_functions(keyvault_bp)
app.register_functions(logger_bp)
app.register_functions(mcpscore_bp)
app.register_functions(nlpproc_bp)
app.register_functions(rsslistener_bp)

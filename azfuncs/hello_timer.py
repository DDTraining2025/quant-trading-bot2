import logging
import datetime
from azure.functions import Blueprint, TimerRequest

bp = Blueprint()

@bp.function_name(name="HelloTimer")
@bp.timer_trigger(
    name="hello_timer_trigger",
    schedule="0 * * * * *",  # every minute
    run_on_startup=False
)
def hello_function(timer: TimerRequest) -> None:
    now = datetime.datetime.utcnow().isoformat()
    logging.info(f"✅ Hello from Azure! Triggered at {now}")

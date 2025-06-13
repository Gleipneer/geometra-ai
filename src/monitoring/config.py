from pathlib import Path

MONITORING_DIR = Path("monitoring")
LOGGING_DIR = MONITORING_DIR / "logging"
METRICS_DIR = MONITORING_DIR / "metrics"
ALERTS_DIR = MONITORING_DIR / "alerts"

def setup_monitoring():
    """Setup monitoring directories."""
    for directory in [MONITORING_DIR, LOGGING_DIR, METRICS_DIR, ALERTS_DIR]:
        directory.mkdir(exist_ok=True)

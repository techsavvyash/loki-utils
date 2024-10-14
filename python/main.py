from loki_logger import get_loki_logger

logger = get_loki_logger("YourAppName")

logger.info("This is an info message", org_id="org123", bot_id="bot456")
logger.error("An error occurred", org_id="org789", bot_id="bot012", trace="Error stack trace")
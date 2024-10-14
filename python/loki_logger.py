import logging
import json
import time
from typing import Dict, Any, Optional
import requests
from configparser import ConfigParser

class LokiLogger(logging.Logger):
    def __init__(self, name: str, config_file: str = 'config.ini'):
        super().__init__(name)
        self.config = ConfigParser()
        self.config.read(config_file)
        self.loki_url = self.config.get('Loki', 'LOKI_INTERNAL_BASE_URL')
        self.env = self.config.get('App', 'environment')

    def _push_to_loki(self, level: str, message: Any, org_id: str, bot_id: str, context: Optional[str] = None, trace: Optional[str] = None):
        timestamp = int(time.time() * 1e9)  # Convert to nanoseconds
        log_entry = {
            "level": level,
            "message": json.dumps(message) if isinstance(message, dict) else str(message),
            "context": context or self.name,
            "trace": trace
        }

        logs = {
            "streams": [
                {
                    "stream": {
                        "level": level,
                        "env": self.env,
                    },
                    "values": [
                        [
                            str(timestamp),
                            json.dumps(log_entry),
                            {
                                "orgId": org_id,
                                "botId": bot_id,
                            }
                        ]
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.loki_url}/loki/api/v1/push",
                json=logs,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error pushing logs to Loki: {e}")

    def log(self, level: int, msg: Any, *args, **kwargs):
        org_id = kwargs.pop('org_id', 'unknown')
        bot_id = kwargs.pop('bot_id', 'unknown')
        context = kwargs.pop('context', None)
        trace = kwargs.pop('trace', None)

        super().log(level, msg, *args, **kwargs)
        
        level_name = logging.getLevelName(level).lower()
        self._push_to_loki(level_name, msg, org_id, bot_id, context, trace)

    def error(self, msg: Any, *args, **kwargs):
        self.log(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        self.log(logging.WARNING, msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg: Any, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)

def get_loki_logger(name: str, config_file: str = 'config.ini') -> LokiLogger:
    return LokiLogger(name, config_file)

# Usage example
if __name__ == "__main__":
    logger = get_loki_logger("TestLogger")
    logger.info("This is an info message", org_id="org123", bot_id="bot456")
    logger.error("This is an error message", org_id="org789", bot_id="bot012", trace="Error trace")
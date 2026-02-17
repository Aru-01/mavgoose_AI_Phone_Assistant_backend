import requests
import logging
from decouple import config

logger = logging.getLogger(__name__)
AI_SYSTEM_URL = config("AI_SYSTEM_URL")


def trigger_ai_system_update():
    try:
        requests.post(AI_SYSTEM_URL, timeout=5)
    except Exception as e:
        logger.error(f"AI system update failed: {str(e)}")

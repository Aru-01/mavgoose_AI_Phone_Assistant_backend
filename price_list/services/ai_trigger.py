import requests
import logging
from decouple import config

logger = logging.getLogger(__name__)

AI_RAG_URL = config("AI_RAG_URL")


def trigger_ai_rag_update():
    try:
        requests.post(AI_RAG_URL, timeout=5)
    except Exception as e:
        logger.error(f"AI RAG trigger failed: {str(e)}")

import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LMS_SERVICE_URL = os.environ.get("LMS_SERVICE_URL", "http://localhost:8002")
LMS_SERVICE_KEY = os.environ.get("LMS_SERVICE_KEY", "")


def handle_schedule(event: dict, context) -> dict:
    """Trigger: EventBridge schedule — llama POST /lms/sync en ms-integracion-lms."""
    logger.info("Iniciando sincronización Moodle | event=%s", json.dumps(event))

    url = f"{LMS_SERVICE_URL}/lms/sync"
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json", "X-Service-Key": LMS_SERVICE_KEY},
        data=b"{}",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
            logger.info("Sincronización completada | resultado=%s", body)
            return {"statusCode": 200, "body": body}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        logger.error("Error HTTP en sync | status=%s | body=%s", e.code, error_body)
        raise RuntimeError(f"Sync falló con HTTP {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        logger.error(
            "Error de conexión al ms-integracion-lms | url=%s | reason=%s",
            url,
            e.reason,
        )
        raise RuntimeError(f"No se pudo conectar a {url}: {e.reason}") from e


# Alias para AWS Lambda
lambda_handler = handle_schedule

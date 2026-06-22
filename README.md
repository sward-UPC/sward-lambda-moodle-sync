# sward-lambda-moodle-sync

AWS Lambda del sistema **SWARD** que dispara periódicamente la ingesta de datos
académicos desde **Moodle LMS**.

No realiza la sincronización por sí misma: actúa como **disparador delgado** (thin
trigger) que invoca al microservicio `sward-ms-integracion-lms`, el cual hace el
trabajo real de leer Moodle y persistir cursos, actividades, calificaciones e
interacciones.

## Qué hace

1. Se ejecuta por schedule (cada 15 minutos).
2. Hace `POST /lms/sync` contra `ms-integracion-lms`, con cuerpo `{}` y la cabecera
   de autenticación `X-Service-Key`.
3. Registra el resultado y devuelve `{ "statusCode": 200, "body": <resultado> }`.
4. Ante error HTTP o de conexión, **lanza una excepción** para que EventBridge
   reintente la invocación.

## Trigger

**Amazon EventBridge** — regla de schedule `rate(15 minutes)`
(`sward-moodle-sync-schedule`, definida en `template.yaml`).

## A qué llama

| | |
|---|---|
| Destino | `sward-ms-integracion-lms` |
| Endpoint | `POST {LMS_SERVICE_URL}/lms/sync` |
| Cuerpo | `{}` |
| Auth | cabecera `X-Service-Key: {LMS_SERVICE_KEY}` |
| Timeout cliente | 280 s (el timeout del lambda es 300 s) |

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `LMS_SERVICE_URL` | sí | URL base de `ms-integracion-lms` (p. ej. el DNS interno de Cloud Map o el ALB). Por defecto `http://localhost:8002`. |
| `LMS_SERVICE_KEY` | sí (prod) | Clave de servicio enviada en `X-Service-Key`. En el SAM template es un parámetro `NoEcho`. Recomendado: provisionarla desde Secrets Manager / SSM en producción. |
| `LOG_LEVEL` | no | Nivel de log (`INFO` por defecto). |

No hay secretos hardcodeados en el código; todo se inyecta por entorno.

## Stack

- Python 3.11
- **Solo biblioteca estándar** (`urllib`, `json`, `logging`) — `requirements.txt`
  está vacío, sin dependencias externas en runtime.
- Empaquetado como **imagen de contenedor** (`Dockerfile`, base
  `public.ecr.aws/lambda/python:3.11`).
- Infraestructura local/declarativa: AWS SAM (`template.yaml`).

## Estructura

```
handler.py            # handle_schedule() — alias lambda_handler. POST /lms/sync con urllib
lib/
  logger.py           # logger JSON estructurado para CloudWatch (utilitario compartido)
tests/
  test_handler.py     # tests unitarios del handler (urlopen mockeado)
Dockerfile            # imagen Lambda para ECR/GHCR
template.yaml         # AWS SAM: función + schedule EventBridge cada 15 min
Makefile              # test | lint | deploy | invoke
requirements.txt      # vacío (stdlib)
requirements-dev.txt  # pytest, pytest-cov, moto, ruff
```

## Construcción y despliegue

El despliegue en la nube es por **imagen de contenedor**. El workflow
`.github/workflows/build-push.yml` construye la imagen y la publica a GHCR/ECR
**al hacer push a la rama `deploy`**:

```bash
git checkout deploy
git merge main
git push origin deploy      # dispara build & push de la imagen
```

Construcción local de la imagen:

```bash
docker build -t sward-lambda-moodle-sync .
```

Despliegue local con SAM (entornos efímeros / pruebas):

```bash
make deploy
# equivale a: sam build && sam deploy --guided
# parámetros: LmsServiceUrl, LmsServiceKey
```

## Cómo testear

```bash
make test          # pip install -r requirements-dev.txt && pytest tests/ -v
# o directamente:
pytest -q
```

Lint y formato:

```bash
make lint          # ruff check . && ruff format --check .
```

Invocación local (requiere `events/schedule.json`):

```bash
make invoke        # sam local invoke MoodleSyncFunction --event events/schedule.json
```

Los tests cubren: sync exitoso, error HTTP (5xx/4xx), error de conexión
(`URLError`) y respuesta con JSON malformado. `urlopen` se mockea, no se hace red real.

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)
Taller de Proyecto 1 / 2026

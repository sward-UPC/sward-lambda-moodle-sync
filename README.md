# sward-lambda-moodle-sync

AWS Lambda del sistema **SWARD** que sincroniza periódicamente los datos académicos desde **Moodle LMS**.

## Trigger

**Amazon EventBridge** schedule — se ejecuta cada 15 minutos.

## Acción

Llama a `POST /lms/sync` en el microservicio `sward-ms-integracion-lms` para actualizar cursos, actividades, calificaciones e interacciones desde Moodle.

## Estructura

```
handler.py          # LambdaMoodleHandler.handle_schedule()
lib/
  db_client.py      # psycopg3 directo (sin ORM)
  logger.py         # Structured JSON logger para CloudWatch
requirements.txt
template.yaml       # AWS SAM template
Makefile            # make deploy | make test | make invoke
```

## Stack

- Python 3.11 · boto3 · httpx · AWS SAM

## Despliegue

```bash
make deploy ENV=staging
```

## Tests

```bash
make test
```

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)  
Taller de Proyecto 1 / 2026

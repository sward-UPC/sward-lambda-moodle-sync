# PROGRESS — sward-lambda-moodle-sync

## Sprint 2 — 2026-05-29

### Implementado
- [x] handler.py — llama POST /lms/sync con urllib (sin deps externas)
- [x] lib/logger.py — JSON logger para CloudWatch
- [x] Tests: sync exitoso, error HTTP, error conexión
- [x] template.yaml — AWS SAM con EventBridge schedule cada 15 min
- [x] Makefile — test, lint, deploy, invoke
- [x] GitHub Actions CI

### Pendiente
- [ ] events/schedule.json para sam local invoke

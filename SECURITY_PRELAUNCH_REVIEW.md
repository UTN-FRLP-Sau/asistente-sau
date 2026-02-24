# Revisión de seguridad y mejoras pre-publicación

Fecha: 2026-02-24  
Alcance: `chatbot/` (Rasa, actions, conectores, despliegue Docker/K8s, web estática)

## Resumen ejecutivo

Se identificaron riesgos relevantes antes de una publicación oficial:

1. **Exposición amplia de la API y CORS permisivo** (alto).
2. **Webhook de WhatsApp sin validación criptográfica de origen** (alto).
3. **Infraestructura con configuraciones inseguras por defecto** (Redis sin auth/TLS, `latest`, `hostPath`) (medio-alto).
4. **Riesgo operativo de denegación de servicio por I/O bloqueante en código async** (medio).
5. **Falta de hardening de contenedores y controles de red** (medio).

## Hallazgos principales

### 1) API de Rasa expuesta con CORS global
- En `docker-compose`, Rasa se inicia con `--enable-api` y `--cors "*"`, exponiendo la API administrativa y permitiendo orígenes amplios.  
- En `endpoints.yml` también se permite `cors_origins: ["*"]`.

**Riesgo:** abuso de endpoints administrativos, cross-origin no deseado, ampliación de superficie de ataque.

**Evidencia:**
- `chatbot/docker-compose.yml`
- `chatbot/endpoints.yml`

**Mitigación recomendada:**
- Restringir CORS a dominios exactos de producción.
- Evitar `--enable-api` en internet pública o protegerlo detrás de gateway con auth (JWT/API key/mTLS).
- Separar endpoint público de webhooks del endpoint admin.

### 2) Webhook de WhatsApp sin validación de firma (`X-Hub-Signature-256`)
- El conector valida `verify_token` en el GET de suscripción, pero en POST no verifica firma HMAC del payload.

**Riesgo:** posible spoofing de eventos al webhook si es accesible públicamente.

**Evidencia:**
- `chatbot/custom_components/whatsapp_connector.py`

**Mitigación recomendada:**
- Verificar `X-Hub-Signature-256` con App Secret en cada POST.
- Rechazar requests sin firma o con timestamp fuera de ventana.

### 3) Llamadas HTTP bloqueantes dentro de métodos async
- Se usa `requests.post(...)` dentro de métodos `async def` en el output channel.

**Riesgo:** bloqueo de event loop, degradación y posible DoS bajo carga.

**Evidencia:**
- `chatbot/custom_components/whatsapp_connector.py`

**Mitigación recomendada:**
- Migrar a cliente async (`httpx.AsyncClient`/`aiohttp`) con timeouts, retries y circuit breaker.
- Limitar tamaño y frecuencia de mensajes salientes.

### 4) Redis sin autenticación/TLS y puertos publicados
- En local se publica `6379:6379`; en endpoints/deploy no se observa password/TLS.

**Riesgo:** acceso no autorizado al lock/tracker store, manipulación de sesiones.

**Evidencia:**
- `chatbot/docker-compose.yml`
- `chatbot/endpoints.yml`
- `chatbot/deployment/redis-service.yaml` y `chatbot/deployment/redis-deployment.yaml`

**Mitigación recomendada:**
- Redis con contraseña, bind privado, NetworkPolicy y TLS cuando aplique.
- No publicar puertos de datos sin necesidad.

### 5) Uso de imágenes `latest`
- Se utiliza `manuelmorullo/rasa-chatbot:latest` en varios manifiestos.

**Riesgo:** deriva de versión, deployments no reproducibles y exposición involuntaria a cambios inseguros.

**Evidencia:**
- `chatbot/docker-compose.yml`
- `chatbot/deployment/rasa-deployment.yaml`
- `chatbot/deployment/rasa-actions-deployment.yaml`

**Mitigación recomendada:**
- Fijar digest (`@sha256`) o tags inmutables versionadas.
- Pipeline con escaneo de imágenes (Trivy/Grype/Snyk).

### 6) Dependencia de `hostPath` en Kubernetes
- Se montan rutas del host para modelos/actions.

**Riesgo:** acoplamiento fuerte al nodo, exposición de filesystem del host y menor portabilidad/seguridad.

**Evidencia:**
- `chatbot/deployment/rasa-deployment.yaml`
- `chatbot/deployment/rasa-actions-deployment.yaml`

**Mitigación recomendada:**
- Migrar a PVC/objet storage (S3/MinIO) y usar init containers o sidecars controlados.

### 7) Hardening de contenedores incompleto
- No se observan `securityContext`, `runAsNonRoot`, `readOnlyRootFilesystem`, seccomp/cap drop.

**Riesgo:** mayor impacto ante compromisos del contenedor.

**Evidencia:**
- `chatbot/deployment/*.yaml`

**Mitigación recomendada:**
- Agregar pod/container security context, capacidades mínimas y políticas de admisión.

### 8) Manejo de errores/logs mejorable en webhook
- Excepción global con `logger.error` sin tipificar ni correlación; no hay trazabilidad de seguridad.

**Riesgo:** pérdida de observabilidad ante incidentes.

**Evidencia:**
- `chatbot/custom_components/whatsapp_connector.py`

**Mitigación recomendada:**
- Logging estructurado con request-id, sender-id anonimizado y métricas de rechazo/errores.
- Alertas por ratios de 4xx/5xx anómalos.

## Oportunidades de mejora no estrictamente de seguridad

- **Calidad operativa:** healthchecks/readiness/liveness en Docker/K8s y budgets de recursos por entorno.
- **Confiabilidad:** timeouts y retries explícitos para llamadas externas.
- **Gobernanza de dependencias:** lockfiles, política de actualización y SBOM.
- **Cumplimiento/privacidad:** política de retención de conversaciones y minimización de PII.
- **Testing:** pruebas de carga y de abuso (payload malicioso, rate limits, replay attacks).

## Plan recomendado (priorizado)

### 0-7 días (bloqueantes de salida)
1. Restringir CORS y proteger/deshabilitar `--enable-api` público.
2. Validar firma de Meta en webhook POST.
3. Quitar exposición innecesaria de puertos (especialmente Redis).
4. Fijar versión inmutable de imágenes.

### 1-3 semanas
1. Migrar cliente HTTP a async con timeouts/retries.
2. Endurecer Kubernetes (`securityContext`, NetworkPolicies, secretos en K8s Secrets).
3. Sustituir `hostPath` por PVC/obj storage.

### 1-2 meses
1. Pipeline de seguridad (SAST, escaneo de contenedores, IaC scan, dependencia/SBOM).
2. Observabilidad de seguridad y runbooks de incident response.
3. Pruebas regulares de penetración y threat modeling ligero.

## Checklist de salida a producción

- [ ] CORS limitado a dominios oficiales.
- [ ] API admin no expuesta públicamente sin autenticación fuerte.
- [ ] Webhook con validación de firma y anti-replay.
- [ ] Redis privado, autenticado y con controles de red.
- [ ] Imágenes fijadas por digest y escaneadas en CI.
- [ ] Contenedores con mínimos privilegios.
- [ ] Políticas de secretos, retención de datos y backups.
- [ ] Monitoreo + alertas + playbooks de respuesta.

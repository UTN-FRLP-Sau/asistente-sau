#!/bin/bash

# Verifico que se haya pasado un parametro al script, como la URL de ngrok
if [ -z "$1" ]; then
  echo "Uso: $0 <URL_WEBHOOK>"
  echo "Ejemplo: $0 https://abcd-1234.ngrok-free.app"
  exit 1
fi

# Guardo la URL base que se pasa como argumento en una variable
WEBHOOK_URL="$1"

echo "Voy a usar esta URL para el webhook: $WEBHOOK_URL"

# Antes de seguir, necesito obtener el TELEGRAM_TOKEN del secret que ya tengo en Kubernetes
echo "Buscando el TELEGRAM_TOKEN en el secret 'telegram-secrets'..."
TELEGRAM_TOKEN=$(kubectl get secret telegram-secrets -o jsonpath='{.data.TELEGRAM_TOKEN}' | base64 --decode)

# Si el token no se pudo obtener, muestro un error y salgo del script
if [ -z "$TELEGRAM_TOKEN" ]; then
  echo "Error: No se encontró el TELEGRAM_TOKEN en el secret 'telegram-secrets'. ¡Revisa que el secret exista y que la clave 'TELEGRAM_TOKEN' esté bien!"
  exit 1
fi
echo "¡Listo! TELEGRAM_TOKEN obtenido."

# 1. Actualizo el ConfigMap de Rasa para que sepa la URL correcta de su webhook
echo "Actualizando el ConfigMap 'rasa-credentials-cm' para que Rasa apunte a la URL del webhook..."
kubectl get configmap rasa-credentials-cm -o yaml | \
sed -E "s#^(\s*webhook_url: ).*#\1\"${WEBHOOK_URL}/webhook\"#" | \
kubectl apply -f -

# 2. Actualizo el Secret de Telegram con el nombre de usuario del bot, el token y la URL completa del webhook
echo "Actualizando el Secret 'telegram-secrets' con la URL completa del webhook de Telegram..."
TELEGRAM_BOT_USERNAME=$(kubectl get secret telegram-secrets -o jsonpath='{.data.TELEGRAM_BOT_USERNAME}' | base64 --decode)

kubectl create secret generic telegram-secrets \
  --namespace=default \
  --from-literal=TELEGRAM_BOT_USERNAME="${TELEGRAM_BOT_USERNAME}" \
  --from-literal=TELEGRAM_TOKEN="${TELEGRAM_TOKEN}" \
  --from-literal=TELEGRAM_WEBHOOK_URL="${WEBHOOK_URL}/webhooks/telegram/webhook" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Le digo a la API de Telegram cual es la URL del bot para que le envie las actualizaciones
echo "Configurando el webhook en la API de Telegram para que envíe los mensajes a la URL correcta..."
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
  -d "url=${WEBHOOK_URL}/webhooks/telegram/webhook"

echo "Webhook actualizado correctamente."

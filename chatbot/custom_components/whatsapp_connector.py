import logging
import hashlib
import hmac
import requests
from sanic import Blueprint, response
from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage

logger = logging.getLogger(__name__)

class WhatsAppOutput(OutputChannel):
    """Maneja el envío de mensajes desde Rasa hacia WhatsApp"""
    @classmethod
    def name(cls):
        return "whatsapp"

    def __init__(self, access_token, phone_number_id):
        self.access_token = access_token
        self.phone_number_id = phone_number_id

    async def send_text_message(self, recipient_id, text, **kwargs):
        """Envía mensajes de texto plano"""
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": text},
        }
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            logger.error(f"Error enviando texto a WhatsApp: {r.text}")

    async def send_text_with_buttons(self, recipient_id, text, buttons, **kwargs):
        """Traduce los botones de Rasa a botones de respuesta rápida de WhatsApp (máx 3)"""
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        whatsapp_buttons = []
        for b in buttons[:3]:
            whatsapp_buttons.append({
                "type": "reply",
                "reply": {
                    "id": b.get("payload"),
                    "title": b.get("title")[:20] 
                }
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": whatsapp_buttons}
            }
        }
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            logger.error(f"Error enviando botones a WhatsApp: {r.text}")

    async def send_custom_json(self, recipient_id, json_message, **kwargs):
        """
        NUEVO: Permite enviar payloads complejos (como Listas) desde las Actions
        usando dispatcher.utter_message(json_message=...)
        """
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        # Inyectamos el destinatario y el producto en el payload si no vienen
        json_message["messaging_product"] = "whatsapp"
        json_message["to"] = recipient_id
        
        r = requests.post(url, headers=headers, json=json_message)
        if r.status_code != 200:
            logger.error(f"Error enviando Custom JSON a WhatsApp: {r.text}")

class WhatsAppInput(InputChannel):
    """Maneja la recepción de mensajes desde WhatsApp hacia Rasa"""
    @classmethod
    def name(cls):
        return "whatsapp_connector.WhatsAppInput"

    def __init__(self, access_token, phone_number_id, verify_token, app_secret):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self.app_secret = app_secret

    def _is_valid_signature(self, request) -> bool:
        """Valida la firma X-Hub-Signature-256 enviada por Meta."""
        if not self.app_secret:
            logger.error("Falta app_secret para validar firma del webhook de WhatsApp.")
            return False

        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature.startswith("sha256="):
            logger.warning("Webhook rechazado: header X-Hub-Signature-256 ausente o inválido.")
            return False

        incoming_digest = signature.split("=", 1)[1]
        expected_digest = hmac.new(
            self.app_secret.encode("utf-8"),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(incoming_digest, expected_digest):
            logger.warning("Webhook rechazado: firma HMAC inválida.")
            return False

        return True

    @classmethod
    def from_credentials(cls, credentials):
        if not credentials:
            cls.raise_missing_credentials_error()

        return cls(
            access_token=credentials.get("access_token"),
            phone_number_id=credentials.get("phone_number_id"),
            verify_token=credentials.get("verify_token"),
            app_secret=credentials.get("app_secret"),
        )

    def blueprint(self, on_new_message):
        custom_webhook = Blueprint("whatsapp_webhook", __name__)

        @custom_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["GET"])
        async def verify(request):
            query = request.args
            if query.get("hub.mode") == "subscribe" and query.get("hub.verify_token") == self.verify_token:
                return response.text(query.get("hub.challenge"))
            return response.text("Error de verificación", 403)

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request):
            if not self._is_valid_signature(request):
                return response.text("Firma inválida", 403)

            payload = request.json
            try:
                entry = payload.get("entry", [{}])[0]
                changes = entry.get("changes", [{}])[0]
                value = changes.get("value", {})
                messages = value.get("messages", [])
                
                if messages:
                    message = messages[0]
                    sender_id = message.get("from")
                    text = None
                    msg_type = message.get("type")

                    # 1. Mensaje de Texto Simple
                    if msg_type == "text":
                        text = message.get("text", {}).get("body")
                    
                    # 2. Mensaje Interactivo (Botones o Listas)
                    elif msg_type == "interactive":
                        interactive = message.get("interactive", {})
                        int_type = interactive.get("type")
                        
                        if int_type == "button_reply":
                            # Clic en botones de respuesta rápida (máx 3)
                            text = interactive.get("button_reply", {}).get("id")
                        elif int_type == "list_reply":
                            # Clic en una opción de la LISTA (máx 10)
                            text = interactive.get("list_reply", {}).get("id")

                    if text and sender_id:
                        out_channel = WhatsAppOutput(self.access_token, self.phone_number_id)
                        # Enviamos el 'id' del botón/lista como si fuera el texto del usuario
                        await on_new_message(UserMessage(text, out_channel, sender_id, input_channel=self.name()))
            
            except Exception as e:
                logger.error(f"Error procesando mensaje de WhatsApp: {e}")
            
            return response.text("ok")

        return custom_webhook

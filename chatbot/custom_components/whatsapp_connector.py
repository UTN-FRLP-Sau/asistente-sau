import logging
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
        """Traduce los botones de Rasa a botones de respuesta de WhatsApp (máx 3)"""
        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        # WhatsApp solo permite hasta 3 botones de respuesta rápida
        whatsapp_buttons = []
        for b in buttons[:3]:
            whatsapp_buttons.append({
                "type": "reply",
                "reply": {
                    "id": b.get("payload"),
                    "title": b.get("title")[:20] # Límite de 20 caracteres
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

class WhatsAppInput(InputChannel):
    """Maneja la recepción de mensajes desde WhatsApp hacia Rasa"""
    @classmethod
    def name(cls):
        return "whatsapp_connector.WhatsAppInput"

    def __init__(self, access_token, phone_number_id, verify_token):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token

    @classmethod
    def from_credentials(cls, credentials):
        """Este método es VITAL para que Rasa cargue las credenciales del credentials.yml"""
        if not credentials:
            cls.raise_missing_credentials_error()

        return cls(
            access_token=credentials.get("access_token"),
            phone_number_id=credentials.get("phone_number_id"),
            verify_token=credentials.get("verify_token")
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
            payload = request.json
            try:
                entry = payload.get("entry", [{}])[0]
                changes = entry.get("changes", [{}])[0]
                value = changes.get("value", {})
                message = value.get("messages", [{}])[0]
                
                if message:
                    sender_id = message.get("from")
                    text = None

                    # Detectar si es un mensaje de texto normal o un clic en un botón
                    if message.get("type") == "text":
                        text = message.get("text", {}).get("body")
                    elif message.get("type") == "interactive":
                        # Captura el payload del botón clickeado
                        text = message.get("interactive", {}).get("button_reply", {}).get("id")

                    if text and sender_id:
                        out_channel = WhatsAppOutput(self.access_token, self.phone_number_id)
                        await on_new_message(UserMessage(text, out_channel, sender_id, input_channel=self.name()))
            except Exception as e:
                logger.error(f"Error procesando mensaje de WhatsApp: {e}")
            
            return response.text("ok")

        return custom_webhook
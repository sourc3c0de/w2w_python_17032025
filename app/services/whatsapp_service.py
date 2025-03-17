import requests
import logging
from typing import Dict, Any
from app.config import settings
from app.models.whatsapp_model import (
    WhatsAppMessage,
    WhatsAppSendMessage,
    WhatsAppTextContent
)

logger = logging.getLogger(__name__)

class WhatsAppService:
    """ Servicio para interactuar con la API de WhatsApp """
    
    @staticmethod
    async def process_message(message: Dict[str, Any], metadata: Dict[str, Any]):
        """ Procesa los mensajes entrantes de WhatsApp """
        try:
            message_type = message.get("type")
            from_number_id = message.get("phone_number_id")
            sender_number = message.get("from")
            
            logger.info(f"Processing message from {sender_number} with type {message_type}")
            
            if message_type == "text" and "text" in message:
                text = message.get("text", {}).get("body")
                
                logger.info(f"Received text message: {text}")
                
                # Aquí puedes implementar la lógica para procesar el mensaje
                # Por ejemplo, integración con NLP, base de datos, etc.
                
                # Enviar respuesta
                await WhatsAppService.send_message(sender_number, f"Echo: {text}")
            else:
                logger.warning(f"Unsupported message type: {message_type}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            
    @staticmethod
    async def process_status_update(status: Dict[str, Any]):
        """ Procesa las actualizaciones de estado de los mensajes """
        try:
            logger.info(
                f"Message status update - ID: {status.get('id')}, "
                f"Status: {status.get('status')}, "
                f"Timestamp: {status.get('timestamp')}, "
                f"Recipient ID: {status.get('recipient_id')}"
            )
            
            # Aquí puedes implementar la lógica para manejar diferentes estados
            # como 'sent', 'delivered', 'read', etc.
            
            status_value = status.get('status')
            if status_value == "delivered":
                # Aquí puedes implementar la lógica para manejar el estado 'delivered'
                pass
            elif status_value == "read":
                # Aquí puedes implementar la lógica para manejar el estado 'read'
                pass
            elif status_value == "sent":
                # Aquí puedes implementar la lógica para manejar el estado 'sent'
                pass
            else:
                logger.warning(f"Unknown status: {status_value}")
                
        except Exception as e:
            logger.error(f"Error processing status update: {str(e)}", exc_info=True)
            
    @staticmethod
    async def send_message(recipient_id: str, message_text: str):
        """ Envía un mensaje a través de la API de WhatsApp """
        url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        message = WhatsAppSendMessage(
            to=recipient_id,
            text=WhatsAppTextContent(body=message_text)
        )
        
        try:
            response = requests.post(url, headers=headers, json=message.model_dump(by_alias=True))
            response.raise_for_status()
            logger.info(f"Message sent successfully to {recipient_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return {"error": str(e)}
        
    @staticmethod
    def verify_webhook_token(mode: str, token: str) -> bool:
        """Verifica si el token del webhook es válido"""
        return mode == "subscribe" and token == settings.VERIFY_TOKEN
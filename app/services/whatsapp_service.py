import requests
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.config import settings
from app.repositories.contact_repository import ContactRepository
from app.repositories.message_repository import MessageRepository
from app.models.whatsapp_model import (
    WhatsAppSendMessage,
    WhatsAppTextContent
)

logger = logging.getLogger(__name__)

class WhatsAppService:
    """ Servicio para interactuar con la API de WhatsApp """
    
    @staticmethod
    async def process_message(message: Dict[str, Any], value: Dict[str, Any], db: Session):
        """ Procesa los mensajes entrantes de WhatsApp """
        try:
            message_type = message.get("type")
            sender_id = message.get("from")
            wa_message_id = message.get("id")
            timestamp_str = message.get("timestamp")
            
            # Convertir timestamp a datetime
            timestamp = datetime.fromtimestamp(int(timestamp_str)) if timestamp_str else datetime.now(timezone.utc)
            
            # Obtener información de perfil si está disponible
            profile_name = "Unknown"
            try:
                # Los contactos están directamente en 'value', no en 'metadata'
                contacts = value.get("contacts", [])
                if contacts:
                    for contact_info in contacts:
                        if contact_info.get("wa_id") == sender_id:
                            # Extraer el nombre del perfil
                            profile_name = contact_info.get("profile", {}).get("name", "Unknown")
                            break
            except Exception as e:
                logger.warning(f"Error extracting profile info: {e}", exc_info=True)
            
            # Obtener o crear contacto
            contact = ContactRepository.get_or_create(db, sender_id, sender_id, profile_name)
            
            # Procesar según tipo de mensaje
            content = ""
            if message_type == "text" and "text" in message:
                content = message.get("text", {}).get("body", "")
                logger.info(f"Received text message from {sender_id}: {content}")
            else:
                content = f"Mensaje de tipo {message_type} recibido"
                logger.info(f"Received non-text message: {message_type}")
            
            # Guardar mensaje en base de datos
            MessageRepository.create(
                db=db,
                wa_message_id=wa_message_id,
                contact_id=contact.id,
                direction="incoming",
                message_type=message_type,
                content=content,
                timestamp=timestamp,
                status="received"
            )
            
            # Responder con un simple eco (sin OpenAI)
            if message_type == "text":
                response_text = f"Echo: {content}"
                # Enviar respuesta
                response_data = await WhatsAppService.send_message(sender_id, response_text)
                
                # Guardar mensaje de respuesta en BD
                if response_data and "messages" in response_data:
                    outgoing_wa_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                    MessageRepository.create(
                        db=db,
                        wa_message_id=outgoing_wa_id,
                        contact_id=contact.id,
                        direction="outgoing",
                        message_type="text",
                        content=response_text,
                        timestamp=datetime.now(timezone.utc),
                        status="sent"
                    )
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
    
    @staticmethod
    async def process_status_update(status: Dict[str, Any], db: Session):
        """ Procesa las actualizaciones de estado de los mensajes """
        try:
            wa_message_id = status.get("id")
            status_value = status.get("status")
            
            # Actualizar estado del mensaje en la base de datos
            MessageRepository.update_status(db, wa_message_id, status_value)
            
            logger.info(f"Updated message status: {wa_message_id} -> {status_value}")
            
            status_value = status.get('status')
            if status_value == "delivered":
                # Lógica para mensajes entregados
                pass
            elif status_value == "read":
                # Lógica para mensajes leídos
                pass
            elif status_value == "sent":
                # Lógica para mensajes enviados
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
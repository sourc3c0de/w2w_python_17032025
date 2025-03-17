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
from app.services.gemini_service import GeminiService
# Importar el repositorio de sesiones
from app.repositories.session_repository import SessionRepository

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
            
            # Cerrar sesiones inactivas para todos los usuarios (cada vez que alguien envía un mensaje)
            SessionRepository.close_inactive_sessions(db, timeout_minutes=30)
            
            # Obtener o crear una sesión activa para este contacto
            active_session = SessionRepository.get_or_create_active_session(db, contact.id)
            
            # Procesar según tipo de mensaje
            content = ""
            if message_type == "text" and "text" in message:
                content = message.get("text", {}).get("body", "")
                logger.info(f"Received text message from {sender_id}: {content}")
                
                # Verificar si es un comando para cerrar sesión
                if content.lower() in ["/cerrar", "/salir", "/finalizar", "/adios", "/exit", "/close"]:
                    await WhatsAppService.close_user_session(sender_id, db)
                    return  # Terminar aquí, ya no procesamos más
                    
            else:
                content = f"Mensaje de tipo {message_type} recibido"
                logger.info(f"Received non-text message: {message_type}")
            
            # Actualizar actividad de la sesión
            SessionRepository.update_last_activity(db, active_session.id)
            
            # Guardar mensaje en base de datos (ahora con session_id)
            MessageRepository.create(
                db=db,
                wa_message_id=wa_message_id,
                contact_id=contact.id,
                direction="incoming",
                message_type=message_type,
                content=content,
                timestamp=timestamp,
                status="received",
                session_id=active_session.id  # Asociar con la sesión
            )
            
            # Solo procesamos con Gemini si es mensaje de texto
            if message_type == "text":
                # Obtener historial de la SESIÓN actual (no de todo el contacto)
                messages = MessageRepository.get_session_history(db, active_session.id, limit=5)
                
                # Formatear el mensaje para la API de Gemini
                conversation_history = []
                for msg in messages:
                    role = "user" if msg.direction == "incoming" else "assistant"
                    conversation_history.append({
                        "role": role,
                        "content": msg.content
                    })
                
                # Generar respuesta usando Gemini
                ai_response = await GeminiService.generate_response(content, conversation_history)
                
                # Enviar respuesta a través de WhatsApp
                response_data = await WhatsAppService.send_message(sender_id, ai_response)
                                
                # Guardar mensaje de respuesta en BD (con session_id)
                if response_data and "messages" in response_data:
                    outgoing_wa_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                    MessageRepository.create(
                        db=db,
                        wa_message_id=outgoing_wa_id,
                        contact_id=contact.id,
                        direction="outgoing",
                        message_type="text",
                        content=ai_response,
                        timestamp=datetime.now(timezone.utc),
                        status="sent",
                        ai_processed=True,
                        ai_response=ai_response,
                        session_id=active_session.id  # Asociar con la sesión
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

    # Añadir este nuevo método para cerrar sesiones
    @staticmethod
    async def close_user_session(sender_id: str, db: Session):
        """
        Cierra la sesión activa de un usuario, genera un resumen y envía un mensaje de confirmación.
        """
        try:
            # Buscar el contacto
            contact = ContactRepository.get_by_wa_id(db, sender_id)
            
            if not contact:
                logger.warning(f"Intento de cerrar sesión para usuario no encontrado: {sender_id}")
                return {"status": "error", "message": "Usuario no encontrado"}
            
            # Buscar la sesión activa
            active_session = SessionRepository.get_active_session(db, contact.id)
            
            if not active_session:
                await WhatsAppService.send_message(
                    sender_id, 
                    "No tienes una sesión activa en este momento."
                )
                return {"status": "warning", "message": "No hay sesión activa"}
            
            # Obtener los mensajes de la sesión
            messages = MessageRepository.get_session_history(db, active_session.id, limit=20)
            
            # Generar un resumen de la conversación usando Gemini
            conversation_text = ""
            for msg in messages:
                role = "Usuario" if msg.direction == "incoming" else "Asistente"
                conversation_text += f"{role}: {msg.content}\n"
            
            summary_prompt = f"""
            Por favor, genera un resumen conciso de la siguiente conversación entre un usuario y un asistente.
            Resalta: 1) El propósito principal de la conversación, 2) Cualquier decisión o información importante compartida,
            3) Si se completó alguna tarea o transacción. Limita el resumen a 2-3 frases cortas.
            
            Conversación:
            {conversation_text}
            
            Resumen:
            """
            
            session_summary = await GeminiService.generate_response(summary_prompt, [])
            
            # Guardar el resumen en el campo context
            SessionRepository.close_session(
                db, 
                active_session.id, 
                status="closed_by_user",
                context=session_summary
            )
            
            # Enviar mensaje de confirmación
            confirmation_message = (
                "Tu sesión ha sido cerrada correctamente. "
                "Si necesitas ayuda nuevamente, no dudes en escribirnos."
            )
            await WhatsAppService.send_message(sender_id, confirmation_message)
            
            logger.info(f"Sesión {active_session.id} cerrada para {contact.name} con resumen: {session_summary[:50]}...")
            return {"status": "success", "session_id": active_session.id, "summary": session_summary}
        
        except Exception as e:
            logger.error(f"Error cerrando sesión: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
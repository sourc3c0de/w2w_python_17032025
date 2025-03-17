from typing import Dict, Any
import logging
from sqlalchemy.orm import Session
from app.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class WhatsAppController:
    """Controlador para manejar la lógica relacionada con WhatsApp"""
    
    @staticmethod
    async def handle_webhook_data(webhook_data: Dict[str, Any], db: Session):
        """
        Procesa los datos del webhook de WhatsApp
        """
        logger.info(f"Webhook data received: {webhook_data}")
        try:
            if webhook_data.get("object") == "whatsapp_business_account":
                for entry in webhook_data.get("entry", []):
                    for change in entry.get("changes", []):
                        if change.get("field") == "messages":
                            value = change.get("value", {})
                            
                            # Procesar mensajes entrantes
                            if value.get("messages"):
                                for message in value.get("messages", []):
                                    # Pasamos el objeto value completo, no solo metadata
                                    await WhatsAppService.process_message(message, value, db)
                                    
                            # Procesar actualizaciones de estado
                            if value.get("statuses"):
                                for status in value.get("statuses", []):
                                    await WhatsAppService.process_status_update(status, db)
                                    
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error handling webhook data: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str):
        """
        Verifica la solicitud de webhook de WhatsApp
        """
        if WhatsAppService.verify_webhook_token(mode, token):
            return int(challenge)
        else:
            return None
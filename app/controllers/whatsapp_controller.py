from typing import Dict, Any
import logging
from app.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class WhatsAppController:
    """Controlador para manejar la lógica relacionada con WhatsApp"""
    
    @staticmethod
    async def handle_webhook_data(webhook_data: Dict[str, Any]):
        """
        Procesa los datos del webhook de WhatsApp
        """
        try:
            if webhook_data.get("object") == "whatsapp_business_account":
                for entry in webhook_data.get("entry", []):
                    for change in entry.get("changes", []):
                        if change.get("field") == "messages":
                            value = change.get("value", {})
                            
                            # Procesar mensajes entrantes
                            if value.get("messages"):
                                for message in value.get("messages", []):
                                    await WhatsAppService.process_message(message, value.get("metadata", {}))
                                    
                            # Procesar actualizaciones de estado
                            if value.get("statuses"):
                                for status in value.get("statuses", []):
                                    await WhatsAppService.process_status_update(status)
                                    
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
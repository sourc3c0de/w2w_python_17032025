from fastapi import APIRouter, Request, HTTPException
import logging
from app.controllers.whatsapp_controller import WhatsAppController

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"]
)

logger = logging.getLogger(__name__)

# Endpoint para la verificación de webhook de WhatsApp
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    hub_mode = params.get("hub.mode")
    hub_verify_token = params.get("hub.verify_token")
    hub_challenge = params.get("hub.challenge")
    
    logger.info(f"Verifying webhook with mode: {hub_mode}")
    
    result = WhatsAppController.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if result is not None:
        logger.info("Webhook verified successfully")
        return result
    else:
        logger.warning("Verification token mismatch")
        raise HTTPException(status_code=403, detail="Verification token mismatch")
    
# Endpoint para recibir mensajes de WhatsApp
@router.post("/webhook")
async def receive_message(request: Request):
    """Recibe y procesa los eventos del webhook de WhatsApp"""
    try:
        webhook_data = await request.json()
        logger.info("Received webhook data")
        
        return await WhatsAppController.handle_webhook_data(webhook_data)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
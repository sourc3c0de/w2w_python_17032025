import google.generativeai as genai
import logging
from typing import List, Dict
from app.config import settings

logger = logging.getLogger(__name__)

# Configurar API key de Google Gemini
genai.configure(api_key=settings.GOOGLE_GEMINI)

# Definir el prompt del sistema directamente en el código si no está en settings
DEFAULT_SYSTEM_CONTEXT = """
Eres un asistente virtual para un restaurante/servicio de comida.
Puedes ayudar con información sobre el menú, precios, horarios, y tomar pedidos.
Sé amable y entusiasta sobre nuestros platos.
"""

class GeminiService:
    """Servicio para interactuar con la API de Google Gemini."""
    @staticmethod
    async def generate_response(message: str, conversation_hisotory: List[Dict[str, str]] = None) -> str:
        """Genera una respuesta usando Google Gemini basada en el mensaje y el historia de la conversación."""
        try:
            # Inicializar modelo
            model = genai.GenerativeModel(settings.GOOGLE_GEMINI_MODEL)
            
            # Construir un prompt completo que incluya el historial y el contexto del sistema
            system_context = getattr(settings, "GEMINI_SYSTEM_CONTEXT", DEFAULT_SYSTEM_CONTEXT)
            
            # Construir el prompt completo:
            full_prompt = f"{system_context}\n\n"
            
            # Añadir historial de conversación si existe
            if conversation_hisotory:
                full_prompt += "Historial de conversación:\n"
                for msg in conversation_hisotory:
                    role = "Usuario" if msg["role"] == "user" else "Asistente"
                    full_prompt += f"{role}: {msg['content']}\n"
                full_prompt += "\n"
            
            # Añadir el mensaje actual
            full_prompt += f"Usuario: {message}\nAsistente:"
            
            logger.info(f"Prompt enviado a Gemini: {full_prompt}")
            
            # Generar respuesta
            response = model.generate_content(full_prompt, stream=False)
            
            # Obtener respuesta generada
            ai_response = response.text.strip()
            logger.info(f"Respuesta de Gemini: {ai_response}")
            
            return ai_response
        
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return "Lo siento, no puedo procesar tu solicitud en este momento."
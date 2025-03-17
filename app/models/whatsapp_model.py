from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Modelos para mensajes recibidos
class WhatsAppTextMessage(BaseModel):
    body: str

class WhatsAppContact(BaseModel):
    profile: Dict[str, str]
    wa_id: str

class WhatsAppMessageMetadata(BaseModel):
    display_phone_number: str
    phone_number_id: str

class WhatsAppMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: Optional[WhatsAppTextMessage] = None
    type: str

class WhatsAppPricing(BaseModel):
    billable: bool
    pricing_model: str
    category: str

class WhatsAppConversationOrigin(BaseModel):
    type: str

class WhatsAppConversation(BaseModel):
    id: str
    expiration_timestamp: Optional[str] = None
    origin: WhatsAppConversationOrigin

class WhatsAppStatus(BaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation: WhatsAppConversation
    pricing: WhatsAppPricing

class WhatsAppValueMessages(BaseModel):
    messaging_product: str
    metadata: WhatsAppMessageMetadata
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None
    statuses: Optional[List[WhatsAppStatus]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValueMessages
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhookEvent(BaseModel):
    object: str
    entry: List[WhatsAppEntry]


# Modelos para envío de mensajes
class WhatsAppTextContent(BaseModel):
    body: str

class WhatsAppSendMessage(BaseModel):
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    to: str
    type: str = "text"
    text: WhatsAppTextContent
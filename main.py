import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

app = FastAPI(title="Restaurant Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------- Sample restaurant data (for demo chatbot logic) ---------
RESTAURANT = {
    "name": "Blue Flame Bistro",
    "address": "123 Flavor Street, Foodville",
    "phone": "+1 (555) 123-4567",
    "email": "hello@blueflamebistro.com",
    "hours": {
        "monday": "11:00 AM – 9:00 PM",
        "tuesday": "11:00 AM – 9:00 PM",
        "wednesday": "11:00 AM – 9:00 PM",
        "thursday": "11:00 AM – 10:00 PM",
        "friday": "11:00 AM – 11:00 PM",
        "saturday": "10:00 AM – 11:00 PM",
        "sunday": "10:00 AM – 8:00 PM",
    },
    "menu": [
        {"category": "Starters", "items": [
            {"name": "Garlic Parmesan Fries", "price": 7.5, "tags": ["vegetarian"]},
            {"name": "Crispy Calamari", "price": 12.0, "tags": ["seafood"]}
        ]},
        {"category": "Mains", "items": [
            {"name": "Grilled Salmon", "price": 22.0, "tags": ["gluten-free", "seafood"]},
            {"name": "Spicy Chicken Penne", "price": 18.0, "tags": ["spicy"]},
            {"name": "Mushroom Risotto", "price": 17.0, "tags": ["vegetarian", "gluten-free"]}
        ]},
        {"category": "Desserts", "items": [
            {"name": "Classic Tiramisu", "price": 8.0, "tags": []},
            {"name": "Lemon Sorbet", "price": 6.0, "tags": ["vegan", "gluten-free"]}
        ]},
        {"category": "Drinks", "items": [
            {"name": "House Lemonade", "price": 4.0, "tags": ["non-alcoholic"]},
            {"name": "Cold Brew Coffee", "price": 4.5, "tags": ["non-alcoholic"]}
        ]}
    ],
    "services": {
        "delivery": True,
        "takeout": True,
        "reservations": True,
        "dietary": ["vegan", "vegetarian", "gluten-free"]
    }
}


# ----------------------------- Models ------------------------------
class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[ChatMessage]] = Field(default=None, description="Optional prior turns")

class ChatResponse(BaseModel):
    reply: str
    intent: str
    suggestions: List[str] = []
    data: Optional[Dict] = None


# ----------------------------- Helpers -----------------------------
def detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["hour", "open", "closing", "time"]):
        return "hours"
    if any(k in t for k in ["where", "address", "location", "directions"]):
        return "location"
    if any(k in t for k in ["phone", "call", "contact", "email"]):
        return "contact"
    if any(k in t for k in ["menu", "dish", "food", "drink", "dessert", "starter", "main"]):
        return "menu"
    if any(k in t for k in ["book", "reserve", "reservation", "table"]):
        return "reservation"
    if any(k in t for k in ["deliver", "delivery", "takeout", "pickup", "order"]):
        return "ordering"
    if any(k in t for k in ["vegan", "vegetarian", "gluten", "diet", "allergen", "allergy"]):
        return "dietary"
    if any(k in t for k in ["price", "cost", "expensive", "cheap"]):
        return "pricing"
    if any(k in t for k in ["hi", "hello", "hey", "help", "start"]):
        return "greeting"
    return "general"


def handle_intent(intent: str, text: str) -> ChatResponse:
    if intent == "greeting":
        return ChatResponse(
            reply=f"Hi! I'm the {RESTAURANT['name']} assistant. I can help with hours, menu, reservations, delivery, and directions.",
            intent=intent,
            suggestions=["Show me the menu", "What are your hours?", "Book a table", "Do you have vegan options?"]
        )

    if intent == "hours":
        hours_lines = [f"{day.title()}: {hrs}" for day, hrs in RESTAURANT["hours"].items()]
        return ChatResponse(
            reply="Here are our opening hours:\n" + "\n".join(hours_lines),
            intent=intent,
            suggestions=["What's today's schedule?", "Can I book a table?", "Where are you located?"]
        )

    if intent == "location":
        return ChatResponse(
            reply=f"We're at {RESTAURANT['address']}. Parking is available nearby.",
            intent=intent,
            suggestions=["What's your phone number?", "Do you offer delivery?", "Show me the menu"],
            data={"address": RESTAURANT["address"]}
        )

    if intent == "contact":
        return ChatResponse(
            reply=f"You can reach us at {RESTAURANT['phone']} or {RESTAURANT['email']}.",
            intent=intent,
            suggestions=["Book a table", "Opening hours", "Location"]
        )

    if intent == "menu":
        categories = ", ".join([c["category"] for c in RESTAURANT["menu"]])
        return ChatResponse(
            reply=f"Our menu categories are: {categories}. Ask for a category to see items.",
            intent=intent,
            suggestions=["Show starters", "Show mains", "Any vegan options?"],
            data={"menu": RESTAURANT["menu"]}
        )

    if intent == "reservation":
        return ChatResponse(
            reply="We accept reservations for parties of up to 8. Tell me a date, time, and party size and I'll guide you.",
            intent=intent,
            suggestions=["Reserve for 2 tomorrow 7pm", "Do you have outdoor seating?"],
        )

    if intent == "ordering":
        return ChatResponse(
            reply="We offer delivery and takeout via our website and partner apps. What would you like to order?",
            intent=intent,
            suggestions=["Order the Spicy Chicken Penne", "What are popular items?"],
        )

    if intent == "dietary":
        options = ", ".join(RESTAURANT["services"]["dietary"])
        return ChatResponse(
            reply=f"We have dietary-friendly options including: {options}. For example, Lemon Sorbet (vegan, gluten-free) and Mushroom Risotto (vegetarian, gluten-free).",
            intent=intent,
            suggestions=["Show vegan items", "Gluten-free mains", "Any nut-free desserts?"],
        )

    if intent == "pricing":
        return ChatResponse(
            reply="Starters from $7, mains around $17–22, desserts from $6, drinks from $4.",
            intent=intent,
            suggestions=["Show mains", "Any specials today?"],
        )

    # Fallback/general
    return ChatResponse(
        reply="I can help with hours, location, menu details, reservations, delivery, and dietary options. What would you like to know?",
        intent=intent,
        suggestions=["Show me the menu", "What are your hours?", "Book a table"],
    )


# ----------------------------- Routes ------------------------------
@app.get("/")
def read_root():
    return {"message": "Restaurant Chatbot Backend is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/menu")
def get_menu():
    return {"name": RESTAURANT["name"], "menu": RESTAURANT["menu"]}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    intent = detect_intent(req.message)
    response = handle_intent(intent, req.message)
    return response


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

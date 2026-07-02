import os
import re
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv
from knowledge_base import search_faqs
from database import init_db, get_available_slots, book_appointment

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
init_db()

SYSTEM_PROMPT = """You are a helpful assistant for a medical clinic.
Answer ONLY using the clinic information provided in the context below.
If the answer isn't in the context, say you'll connect them with clinic staff — do NOT make up information.
NEVER provide medical diagnosis, treatment advice, or medication suggestions.
If the patient describes symptoms, acknowledge them briefly and recommend booking a consultation — do not assess severity yourself.
Keep responses short and friendly, suitable for WhatsApp."""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

user_sessions = {}

def is_booking_intent(message: str) -> bool:
    keywords = ["book", "appointment", "slot", "schedule", "reserve"]
    return any(word in message.lower() for word in keywords)

def parse_date(message: str) -> str:
    msg = message.lower()
    today = datetime.now()
    if "tomorrow" in msg:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return today.strftime("%Y-%m-%d")

def normalize_time(text: str) -> str:
    """Converts messy time input into the standard format used in slots, e.g. '10:00 AM'."""
    text = text.strip().upper().replace(".", "")
    text = re.sub(r'(\d)(AM|PM)', r'\1 \2', text)
    match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', text)
    if not match:
        return text
    hour = int(match.group(1))
    minute = match.group(2) if match.group(2) else "00"
    meridiem = match.group(3)
    return f"{hour}:{minute} {meridiem}"

def get_response(user_message: str, user_phone: str = "default") -> str:
    session = user_sessions.get(user_phone, {"stage": None})

    # --- Booking flow ---
    if session["stage"] == "awaiting_slot_choice":
        slot_choice = normalize_time(user_message)
        date = session["date"]
        available = get_available_slots(date)

        if slot_choice not in available:
            return f"That slot isn't available. Please choose one of: {', '.join(available)}"

        success = book_appointment(user_phone, date, slot_choice)
        user_sessions[user_phone] = {"stage": None}
        if success:
            return f"✅ Your appointment is confirmed for {date} at {slot_choice}. See you then!"
        else:
            return "Sorry, that slot was just taken. Please try booking again."

    if is_booking_intent(user_message):
        date = parse_date(user_message)
        available = get_available_slots(date)

        if not available:
            return f"Sorry, no slots available on {date}. Please try another day."

        user_sessions[user_phone] = {"stage": "awaiting_slot_choice", "date": date}
        return f"Sure! Available slots for {date}: {', '.join(available)}\nReply with your preferred time (e.g. '11:00 AM')."

    # --- Normal FAQ flow (RAG) ---
    relevant_docs = search_faqs(user_message)
    context = "\n".join(relevant_docs)
    prompt = f"Clinic context:\n{context}\n\nPatient question: {user_message}"
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    print("Clinic chatbot ready. Type 'quit' to exit.\n")
    while True:
        msg = input("Patient: ")
        if msg.lower() in ["quit", "exit"]:
            break
        print("Bot:", get_response(msg))
        print()
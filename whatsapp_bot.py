import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from chatbot import get_response

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "")
    sender = request.form.get("From", "unknown")  # e.g. whatsapp:+91XXXXXXXXXX

    reply_text = get_response(incoming_msg, user_phone=sender)

    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
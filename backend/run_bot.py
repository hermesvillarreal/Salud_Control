import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from sqlmodel import Session, select
from app.database import engine
from app.models import (
    User, WeightRecord, BloodPressureRecord, GlucoseRecord,
    FoodRecord, ClinicalDocument, DocumentType, MealType
)
from app.services.ai_service import analyze_food_text, analyze_food_image

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CONFIRM_FOOD = 1

def parse_time(args: list, start_idx: int) -> datetime:
    """Helper to parse time from command arguments."""
    now = datetime.now()
    if len(args) <= start_idx:
        return now
    
    time_str = args[start_idx]
    try:
        # Handle formats like HH:MM
        if ":" in time_str:
            h, m = map(int, time_str.split(":"))
            return now.replace(hour=h, minute=m, second=0, microsecond=0)
        # Handle relative time like -10m (minutes ago)
        elif time_str.startswith("-") and time_str.endswith("m"):
            mins = int(time_str[1:-1])
            from datetime import timedelta
            return now - timedelta(minutes=mins)
    except Exception:
        pass
    return now

async def get_user_by_chat_id(chat_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.telegram_chat_id == chat_id)
        return session.exec(statement).first()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "¡Hola! Para usar este bot, primero debes vincular tu cuenta.\n"
            "Ve a la web de Salud Control y obtén tu código de vinculación."
        )
        return

    token = args[0]
    with Session(engine) as session:
        statement = select(User).where(User.telegram_auth_token == token)
        user = session.exec(statement).first()

        if user:
            user.telegram_chat_id = chat_id
            user.telegram_auth_token = None  # Clear token after use
            session.add(user)
            session.commit()
            await update.message.reply_text(f"¡Bienvenido {user.full_name or user.username}! Tu cuenta ha sido vinculada correctamente.")
        else:
            await update.message.reply_text("Código de vinculación inválido o expirado.")

async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Comandos de Salud Control*\n\n"
        "📈 *Métricas de Salud:*\n"
        "• `/peso <valor>` - Registra tu peso actual (e.g., `/peso 75.5`)\n"
        "• `/presion <sis> <dia>` - Registra tu presión arterial (e.g., `/presion 120 80`)\n"
        "• `/glucosa <valor>` - Registra tu nivel de glucosa (e.g., `/glucosa 95`)\n\n"
        "🥗 *Alimentación:*\n"
        "• Envía un mensaje de texto describiendo lo que comiste (e.g., 'Comí cereal con leche')\n"
        "• Envía una foto de tu comida con o sin descripción.\n"
        "• El bot analizará los nutrientes y te pedirá confirmar el registro.\n\n"
        "📄 *Documentos Clínicos:*\n"
        "• Envía una foto o PDF con la palabra 'lab' o 'receta' en el comentario para guardarlo automáticamente.\n\n"
        "⚙️ *Cuenta:*\n"
        "• `/start <token>` - Vincula tu cuenta de Salud Control.\n"
        "• `/desvincular` - Desvincula tu cuenta de este bot.\n"
        "• `/help` - Muestra este mensaje de ayuda."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def desvincular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("No tienes ninguna cuenta vinculada actualmente.")
        return

    with Session(engine) as session:
        user.telegram_chat_id = None
        session.add(user)
        session.commit()
        await update.message.reply_text("✅ Tu cuenta ha sido desvinculada correctamente. No recibiré más datos de este chat.")

async def peso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        val = float(context.args[0])
        dt = parse_time(context.args, 1)
        with Session(engine) as session:
            record = WeightRecord(user_id=user.id, weight=val, fecha_hora=dt)
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Peso registrado: {val} kg (Hora: {dt.strftime('%H:%M')})")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /peso <valor> [hora (ej. 10:30 or -10m)]")

async def presion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        sis = int(context.args[0])
        dia = int(context.args[1])
        dt = parse_time(context.args, 2)
        with Session(engine) as session:
            record = BloodPressureRecord(user_id=user.id, systolic=sis, diastolic=dia, fecha_hora=dt)
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Presión arterial registrada: {sis}/{dia} (Hora: {dt.strftime('%H:%M')})")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /presion <sistólica> <diastólica> [hora]")

async def glucosa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        val = float(context.args[0])
        dt = parse_time(context.args, 1)
        with Session(engine) as session:
            record = GlucoseRecord(user_id=user.id, glucose_level=val, measurement_type="ayuno", fecha_hora=dt)
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Glucosa registrada: {val} mg/dL (Hora: {dt.strftime('%H:%M')})")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /glucosa <valor> [hora]")

async def handle_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    text = update.message.text or update.message.caption
    if not text:
        return ConversationHandler.END

    await update.message.reply_text("Analizando tu comida... ⏳")
    
    # Check if it's a photo or text
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # Download photo as bytes
        import io
        photo_bytes = await file.download_as_bytearray()
        
        # Determine mime type (Telegram photos are usually jpg)
        mime_type = "image/jpeg"
        
        macros = await analyze_food_image(bytes(photo_bytes), mime_type, text)
    else:
        macros = await analyze_food_text(text)
    
    if "error" in macros:
        await update.message.reply_text("Lo siento, no pude analizar esa comida. Intenta describirla mejor o subir una foto más clara.")
        return ConversationHandler.END

    # Parse time if specified in text
    dt = datetime.now()
    if text:
        # Simple check for HH:MM in text
        import re
        time_match = re.search(r'\b(\d{1,2}:\d{2})\b', text)
        if time_match:
            try:
                h, m = map(int, time_match.group(1).split(":"))
                dt = dt.replace(hour=h, minute=m, second=0, microsecond=0)
            except Exception:
                pass

    food_name = macros.get('food_name', text)
    summary = (
        f"🥗 *Plato Identificado:* {food_name}\n"
        f"⏰ *Hora:* {dt.strftime('%H:%M')}\n\n"
        f"🍔 *Estimación de Nutrientes:*\n"
        f"🔥 Calorías: {macros.get('calories')} kcal\n"
        f"💪 Proteína: {macros.get('protein')} g\n"
        f"🍞 Carbohidratos: {macros.get('carbs')} g\n"
        f"🥑 Grasas: {macros.get('fat')} g\n\n"
        "¿Deseas registrar esto? Sí / No"
    )
    
    context.user_data['pending_food'] = {
        'description': food_name,
        'calories': macros.get('calories'),
        'protein': macros.get('protein'),
        'carbs': macros.get('carbs'),
        'fat': macros.get('fat'),
        'meal_type': macros.get('meal_type', 'merienda_tarde').lower(),
        'fecha_hora': dt
    }

    reply_keyboard = [["Sí", "No"]]
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRM_FOOD

async def confirm_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    text = update.message.text.lower().strip()
    
    if text in ["sí", "si", "s", "yes", "y", "ok"]:
        data = context.user_data.get('pending_food')
        with Session(engine) as session:
            record = FoodRecord(**data, user_id=user.id)
            session.add(record)
            session.commit()
            await update.message.reply_text("✅ Comida registrada correctamente.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        return

    caption = (update.message.caption or "").lower()
    if "lab" in caption or "receta" in caption:
        doc_type = DocumentType.LABORATORIO if "lab" in caption else DocumentType.RECETA
        
        # Download file
        if update.message.document:
            file = await update.message.document.get_file()
            ext = update.message.document.file_name.split('.')[-1]
        elif update.message.photo:
            file = await update.message.photo[-1].get_file()
            ext = "jpg"
        else:
            return

        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{user.id}_{datetime.now().timestamp()}.{ext}"
        await file.download_to_drive(file_path)

        with Session(engine) as session:
            doc = ClinicalDocument(
                user_id=user.id,
                title="Documento vía Telegram",
                document_type=doc_type,
                file_path=file_path,
                notes=caption,
                fecha_hora=datetime.now()
            )
            session.add(doc)
            session.commit()
            await update.message.reply_text(f"✅ Documento ({doc_type}) guardado correctamente.")

if __name__ == '__main__':
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not found.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("peso", peso))
    application.add_handler(CommandHandler("presion", presion))
    application.add_handler(CommandHandler("glucosa", glucosa))
    application.add_handler(CommandHandler("help", helper))
    application.add_handler(CommandHandler("ayuda", helper))
    application.add_handler(CommandHandler("desvincular", desvincular))
    application.add_handler(CommandHandler("unlink", desvincular))

    # Conversation for food registration
    food_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_food),
            MessageHandler(filters.PHOTO & (~filters.CaptionEntity("bot_command")), handle_food)
        ],
        states={
            CONFIRM_FOOD: [MessageHandler(filters.Regex(r"^(?i)(Sí|Si|S|No|N|Yes|Y|Ok)$"), confirm_food)],
        },
        fallbacks=[],
    )
    application.add_handler(food_conv)

    # Document handler
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    print("Bot is running...")
    application.run_polling()

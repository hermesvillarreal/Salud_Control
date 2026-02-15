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
    ConversationFactory,
    filters,
)
from sqlmodel import Session, select
from app.database import engine
from app.models import (
    User, WeightRecord, BloodPressureRecord, GlucoseRecord,
    FoodRecord, ClinicalDocument, DocumentType, MealType
)
from app.services.ai_service import analyze_food_text

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CONFIRM_FOOD = 1

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

async def peso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        val = float(context.args[0])
        with Session(engine) as session:
            record = WeightRecord(user_id=user.id, weight=val)
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Peso registrado: {val} kg")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /peso <valor>")

async def presion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        sis = int(context.args[0])
        dia = int(context.args[1])
        with Session(engine) as session:
            record = BloodPressureRecord(user_id=user.id, systolic=sis, diastolic=dia)
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Presión arterial registrada: {sis}/{dia}")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /presion <sistólica> <diastólica>")

async def glucosa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    try:
        val = float(context.args[0])
        with Session(engine) as session:
            record = GlucoseRecord(user_id=user.id, glucose_level=val, measurement_type="ayuno")
            session.add(record)
            session.commit()
            await update.message.reply_text(f"✅ Glucosa registrada: {val} mg/dL")
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /glucosa <valor>")

async def handle_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if not user:
        await update.message.reply_text("Por favor, usa /start <token> para vincular tu cuenta.")
        return

    text = update.message.text or update.message.caption
    if not text:
        return ConversationFactory.END

    await update.message.reply_text("Analizando tu comida... ⏳")
    macros = await analyze_food_text(text)
    
    if "error" in macros:
        await update.message.reply_text("Lo siento, no pude analizar esa comida. Intenta describirla mejor.")
        return ConversationFactory.END

    summary = (
        f"🍔 *Estimación de Nutrientes:*\n\n"
        f"🔥 Calorías: {macros.get('calories')} kcal\n"
        f"💪 Proteína: {macros.get('protein')} g\n"
        f"🍞 Carbohidratos: {macros.get('carbs')} g\n"
        f"🥑 Grasas: {macros.get('fat')} g\n\n"
        "¿Deseas registrar esto?"
    )
    
    context.user_data['pending_food'] = {
        'description': text,
        'calories': macros.get('calories'),
        'protein': macros.get('protein'),
        'carbs': macros.get('carbs'),
        'fat': macros.get('fat'),
        'meal_type': MealType.SNACK # Default
    }

    reply_keyboard = [["Sí", "No"]]
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CONFIRM_FOOD

async def confirm_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_chat_id(update.effective_chat.id)
    if update.message.text == "Sí":
        data = context.user_data.get('pending_food')
        with Session(engine) as session:
            record = FoodRecord(**data, user_id=user.id)
            session.add(record)
            session.commit()
            await update.message.reply_text("✅ Comida registrada correctamente.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    
    return ConversationFactory.END

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
                notes=caption
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

    # Conversation for food registration
    food_conv = ConversationFactory(
        entry_points=[
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_food),
            MessageHandler(filters.PHOTO & (~filters.CAPTION_ENTITY("bot_command")), handle_food)
        ],
        states={
            CONFIRM_FOOD: [MessageHandler(filters.Regex("^(Sí|No)$"), confirm_food)],
        },
        fallbacks=[],
    )
    application.add_handler(food_conv)

    # Document handler
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    print("Bot is running...")
    application.run_polling()

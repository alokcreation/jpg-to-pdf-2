
import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send JPG images. When finished, type /convert to generate a PDF.")

image_buffer = {}

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in image_buffer:
        image_buffer[chat_id] = []

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_path = f"/tmp/{chat_id}_{len(image_buffer[chat_id])}.jpg"
    await file.download_to_drive(img_path)

    image_buffer[chat_id].append(img_path)
    await update.message.reply_text("Image saved! Send more or type /convert.")

async def convert_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in image_buffer or len(image_buffer[chat_id]) == 0:
        await update.message.reply_text("No images found!")
        return

    images = [Image.open(img).convert("RGB") for img in image_buffer[chat_id]]
    pdf_path = f"/tmp/{chat_id}_output.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    await update.message.reply_document(InputFile(pdf_path))

    image_buffer[chat_id] = []
    await update.message.reply_text("PDF created successfully!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()

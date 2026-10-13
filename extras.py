import logging
import requests
import time
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from groq import Groq
from config import GROQ_API_KEY
from ai_engine import fusion_mode, detect_language
from database import get_user, create_user, increment_ask, add_history

logger = logging.getLogger(__name__)
groq_sync = Groq(api_key=GROQ_API_KEY)

async def handle_voice(update, context):
    user = update.effective_user
    u = get_user(user.id)
    if not u:
        create_user(user.id, user.full_name, user.username or "")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    msg = await update.message.reply_text("Voice sone hoyeche...")
    try:
        voice_file = await update.message.voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()
        bio = BytesIO(bytes(audio_bytes))
        bio.name = "voice.ogg"
        transcription = groq_sync.audio.transcriptions.create(
            file=bio,
            model="whisper-large-v3-turbo",
        )
        text = transcription.text
        if not text:
            await msg.edit_text("Voice bujhte parini, abar cheshta korun.")
            return
        await msg.edit_text("Sunlam: " + text + chr(10) + chr(10) + "Uttor toiri hocche...")
        lang = detect_language(text)
        answer = await fusion_mode(text, lang)
        increment_ask(user.id)
        add_history(user.id, "[Voice] " + text, answer, "voice")
        if len(answer) > 4000:
            await msg.edit_text(answer[:4000])
            await update.message.reply_text(answer[4000:8000])
        else:
            await msg.edit_text(answer)
    except Exception as e:
        logger.error("Voice: " + str(e))
        await msg.edit_text("Voice process kora jayni. Abar cheshta korun.")

async def img_cmd(update, context):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /img a red rose in garden")
        return
    prompt = " ".join(args)
    user = update.effective_user
    await context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
    msg = await update.message.reply_text("Chobi banano hocche...")
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = "https://image.pollinations.ai/prompt/" + encoded + "?width=1024&height=1024&nologo=true&seed=" + str(int(time.time()))
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            await update.message.reply_photo(photo=r.content, caption="Prompt: " + prompt)
            await msg.delete()
            increment_ask(user.id)
            add_history(user.id, "[IMG] " + prompt, "[Image generated]", "img")
        else:
            await msg.edit_text("Chobi banano jayni. Abar cheshta korun.")
    except Exception as e:
        logger.error("Img: " + str(e))
        await msg.edit_text("Chobi banate shomossha hoyeche. Abar cheshta korun.")

import asyncio
import logging
from groq import AsyncGroq
from google import genai
from config import GROQ_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)
groq_client = AsyncGroq(api_key=GROQ_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def detect_language(text):
    for ch in text:
        if '\u0980' <= ch <= '\u09FF':
            return "bn"
    return "en"

async def call_groq(question):
    try:
        r = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="openai/gpt-oss-20b",
        )
        return r.choices[0].message.content
    except Exception as e:
        logger.error("Groq: " + str(e))
        return None

def _gemini_sync(question):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-flash-latest",
            contents=question,
        )
        return response.text
    except Exception as e:
        logger.error("Gemini: " + str(e))
        return None

async def call_gemini(question):
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _gemini_sync, question),
            timeout=15.0
        )
    except asyncio.TimeoutError:
        logger.error("Gemini: timeout")
        return None
    except Exception as e:
        logger.error("Gemini: " + str(e))
        return None

async def fusion_mode(question, lang):
    results = await asyncio.gather(
        call_groq(question),
        call_gemini(question),
        return_exceptions=True,
    )
    g = results[0] if not isinstance(results[0], Exception) else None
    m = results[1] if not isinstance(results[1], Exception) else None
    available = []
    if g:
        available.append("Groq: " + g)
    if m:
        available.append("Gemini: " + m)
    if not available:
        return "All AI failed. Try again later."
    if len(available) == 1:
        return available[0]
    lang_instr = "Bengali with English mix" if lang == "bn" else "English"
    prompt = "You are Fusion AI. Combine these AI answers into 1 perfect answer in " + lang_instr + ". Question: " + question + " Answers: " + " | ".join(available)
    try:
        r = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
        )
        return r.choices[0].message.content
    except Exception as e:
        logger.error("Fusion: " + str(e))
        return available[0]

async def fast_mode(question):
    ans = await call_groq(question)
    return ans or "Groq API failed. Try /fusion or /smart"

async def smart_mode(question):
    ans = await call_gemini(question)
    if not ans:
        ans = await call_groq("Give a smart detailed answer: " + question)
    return ans or "AI failed. Try /fusion or /fast"

async def code_mode(question):
    ans = await call_groq("You are an expert programmer. Solve this coding problem with clear explanation and code examples: " + question)
    return ans or "Code AI failed. Try again."

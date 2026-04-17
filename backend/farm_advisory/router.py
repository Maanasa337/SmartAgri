#!/usr/bin/env python3
"""
Backend/farm_advisory integration router for FastAPI.

This module provides FastAPI endpoints for voice processing, translation,
and AI-powered agricultural advisory using Bhashini and Groq APIs.

Key features:
- Speech-to-text with multilingual support (12 Indian languages)
- Real-time translation English ↔ regional languages
- AI agricultural advisory via Groq LLaMA
- Text-to-speech synthesis in regional languages
- Comprehensive farm planning based on farmer profile
"""

import os
import sys
import base64
import subprocess
import tempfile
import threading
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── IMPORTS ──────────────────────────────────────
try:
    from .index import (
        bhashini_asr_translate,
        bhashini_translate_tts,
        bhashini_translate_text,
        ask_groq,
        calculate_bleu_score,
        prefetch_services,
        get_service_id,
        generate_comprehensive_advisory,
        LANGUAGES,
    )
    BACKEND_OK = True
    print("[✅ farm_advisory.router] Core voice functions imported successfully")
except ImportError as e:
    print(f"[❌ farm_advisory.router] Import failed: {e}")
    print("[❌ farm_advisory.router] Voice endpoints will return 503")
    BACKEND_OK = False
except Exception as e:
    print(f"[❌ farm_advisory.router] Unexpected error during import: {e}")
    BACKEND_OK = False


# ─────────────────────────── LANGUAGE METADATA ──────────────────────────────
NATIVE_NAMES = {
    "hi": "हिन्दी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "bn": "বাংলা",
    "gu": "ગુજરાતી",
    "mr": "मराठी",
    "pa": "ਪੰਜਾਬੀ",
    "or": "ଓଡ଼ିଆ",
    "as": "অসমীয়া",
    "ur": "اردو",
}


# ─────────────────────────── AUDIO CONVERSION ────────────────────────────────
def convert_to_wav(audio_bytes: bytes) -> bytes:
    """
    Convert browser audio formats (WebM/Opus/MP4) to WAV 16kHz mono PCM.
    Uses ffmpeg for format conversion.
    
    Args:
        audio_bytes: Audio data in any format
        
    Returns:
        WAV audio bytes at 16kHz mono, or original if already WAV
    """
    if not audio_bytes or len(audio_bytes) < 10:
        print(f"[⚠️ ffmpeg] Empty or too small audio: {len(audio_bytes)} bytes")
        return audio_bytes

    # Check if already WAV (RIFF header)
    if audio_bytes[:4] == b'RIFF':
        print("[✅ ffmpeg] Input is already WAV")
        return audio_bytes

    print(f"[🔄 ffmpeg] Converting audio ({len(audio_bytes)} bytes)...")

    fd, tmp_in_path = tempfile.mkstemp(suffix='.webm')
    try:
        with os.fdopen(fd, 'wb') as tmp_in:
            tmp_in.write(audio_bytes)
            tmp_in.flush()

        tmp_out_path = tmp_in_path + ".wav"

        # Convert with ffmpeg: any format → WAV 16kHz mono
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', tmp_in_path,
            '-ar', '16000',      # 16kHz
            '-ac', '1',          # mono
            '-f', 'wav',
            tmp_out_path
        ], capture_output=True, timeout=15)

        if result.returncode != 0:
            err = result.stderr.decode()
            print(f"[⚠️ ffmpeg] Conversion failed: {err}")
            return audio_bytes

        with open(tmp_out_path, 'rb') as f:
            out_bytes = f.read()
            print(f"[✅ ffmpeg] Converted: {len(out_bytes)} bytes")
            return out_bytes
    finally:
        for path in [tmp_in_path, tmp_in_path + ".wav"]:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                print(f"[⚠️ ffmpeg] Cleanup error: {e}")


# ─────────────────────────── FASTAPI ROUTER ─────────────────────────────────
router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.get("/health")
async def health():
    """Check voice service health status."""
    return {"status": "ok", "backend": BACKEND_OK, "service": "farm_advisory"}


@router.get("/languages")
async def get_languages():
    """Get list of supported languages."""
    langs = [
        {
            "id": k,
            "name": v[0],
            "code": v[1],
            "native": NATIVE_NAMES.get(v[1], v[0])
        }
        for k, v in LANGUAGES.items()
    ]
    return {"languages": langs}


@router.post("/prefetch")
async def prefetch(request: Request):
    """
    Pre-warm Bhashini service IDs for faster responses.
    
    Request body:
    {
        "lang_code": "ta"  # language code
    }
    """
    if not BACKEND_OK:
        return JSONResponse({"error": "Voice backend not initialized"}, status_code=503)

    data = await request.json()
    lang_code = data.get("lang_code", "hi")
    
    try:
        prefetch_services(lang_code)
        return {"status": "ok", "message": f"Services ready for {lang_code}"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/transcribe")
async def api_transcribe(request: Request):
    """
    Convert speech to text and translate to English.
    
    Request body:
    {
        "audio": "base64_encoded_audio",
        "lang_code": "ta"
    }
    
    Returns:
    {
        "transcribed": "speech in local language",
        "translated": "translated to English"
    }
    """
    if not BACKEND_OK:
        return JSONResponse({"error": "Voice backend not initialized"}, status_code=503)

    data = await request.json()
    audio_b64 = data.get("audio", "")
    lang_code = data.get("lang_code", "ta")

    try:
        audio_raw = base64.b64decode(audio_b64)
        wav_bytes = convert_to_wav(audio_raw)
        transcribed, translated = bhashini_asr_translate(wav_bytes, lang_code)
        return {"transcribed": transcribed, "translated": translated}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[❌ /api/voice/transcribe] {type(e).__name__}: {e}\n{tb}")
        return JSONResponse(
            {"error": str(e), "type": type(e).__name__},
            status_code=500
        )


@router.post("/converse")
async def api_converse(request: Request):
    """
    Full voice-to-voice conversation pipeline.
    
    Steps:
    1. Convert audio (WebM → WAV)
    2. Speech recognition + translation to English
    3. AI advisory generation via Groq
    4. Translate response back to local language + TTS
    
    Request body:
    {
        "audio": "base64_encoded_webm",
        "lang_code": "ta",
        "profile": {optional farmer profile},
        "is_comprehensive": false
    }
    
    Returns:
    {
        "transcribed": "user's speech in local language",
        "translated": "translated to English",
        "answer": "AI response in English",
        "answer_local": "AI response in local language",
        "audio": "base64_encoded_wav_response"
    }
    """
    if not BACKEND_OK:
        return JSONResponse(
            {"error": "Voice backend not initialized"},
            status_code=503
        )

    data = await request.json()
    audio_b64 = data.get("audio", "")
    lang_code = data.get("lang_code", "ta")
    profile = data.get("profile", None)
    is_comprehensive = data.get("is_comprehensive", False)

    try:
        # Convert audio
        audio_raw = base64.b64decode(audio_b64)
        wav_bytes = convert_to_wav(audio_raw)

        # ASR + translate
        transcribed, english = bhashini_asr_translate(wav_bytes, lang_code)

        # AI response
        if profile and is_comprehensive:
            prompt = generate_comprehensive_advisory(profile, english)
        else:
            prompt = english
        
        answer_en = ask_groq(prompt, is_comprehensive=is_comprehensive)

        # Translate + TTS
        answer_local, audio_resp = bhashini_translate_tts(answer_en, lang_code)
        audio_out_b64 = base64.b64encode(audio_resp).decode()

        return {
            "transcribed": transcribed,
            "translated": english,
            "answer": answer_en,
            "answer_local": answer_local,
            "audio": audio_out_b64,
        }

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[❌ /api/voice/converse] {type(e).__name__}: {e}\n{tb}")
        return JSONResponse(
            {"error": str(e), "type": type(e).__name__},
            status_code=500
        )


@router.post("/ask")
async def api_ask(request: Request):
    """
    Get AI agricultural advice for a question.
    
    Request body:
    {
        "question": "how to treat leaf blight?",
        "profile": {optional farmer profile},
        "is_comprehensive": false
    }
    
    Returns:
    {
        "answer": "AI-generated agricultural advice"
    }
    """
    if not BACKEND_OK:
        return JSONResponse(
            {"error": "Voice backend not initialized"},
            status_code=503
        )

    data = await request.json()
    question = data.get("question", "")
    profile = data.get("profile")
    is_comprehensive = data.get("is_comprehensive", False)

    try:
        if profile and is_comprehensive:
            prompt = generate_comprehensive_advisory(profile, question)
        else:
            prompt = question

        answer = ask_groq(prompt, is_comprehensive=is_comprehensive)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/speak")
async def api_speak(request: Request):
    """
    Convert English text to speech in a regional language.
    
    Request body:
    {
        "text": "English text to convert",
        "lang_code": "ta"
    }
    
    Returns:
    {
        "translated": "text in local language",
        "audio": "base64_encoded_wav_audio"
    }
    """
    if not BACKEND_OK:
        return JSONResponse(
            {"error": "Voice backend not initialized"},
            status_code=503
        )

    data = await request.json()
    text_en = data.get("text", "")
    lang_code = data.get("lang_code", "hi")

    try:
        translated_local, audio_bytes = bhashini_translate_tts(text_en, lang_code)
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return {"translated": translated_local, "audio": audio_b64}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/bleu")
async def api_bleu(request: Request):
    """
    Calculate BLEU score for translation quality assessment.
    
    Request body:
    {
        "reference": "reference text",
        "candidate": "candidate translation"
    }
    
    Returns:
    {
        "BLEU-1": 45.2,
        "BLEU-2": 42.1,
        "BLEU-3": 38.5,
        "BLEU-4": 35.2,
        "Average": 40.25
    }
    """
    data = await request.json()
    reference = data.get("reference", "")
    candidate = data.get("candidate", "")

    try:
        scores = calculate_bleu_score(reference, candidate)
        return scores
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/translate-field")
async def api_translate_field(request: Request):
    """
    Translate a text field between languages.
    
    Request body:
    {
        "text": "text to translate",
        "tgt_lang": "ta"  # target language code
    }
    
    Returns:
    {
        "translated": "translated text"
    }
    """
    data = await request.json()
    text = data.get("text", "")
    tgt_lang = data.get("tgt_lang", "hi")

    try:
        translated = bhashini_translate_text(text, "en", tgt_lang)
        return {"translated": translated}
    except Exception as e:
        # Graceful fallback
        return {
            "translated": text,
            "error": str(e),
            "message": "Translation failed, returning original text"
        }


# ─────────────────────────── AUTO-PREFETCH ON STARTUP ──────────────────────
def _startup_prefetch():
    """Warm up Bhashini service IDs for Tamil on startup."""
    if not BACKEND_OK:
        return

    try:
        print("[🔄 farm_advisory.router] Pre-warming Bhashini service IDs...")
        for task, src, tgt in [
            ("asr", "ta", None),
            ("translation", "ta", "en"),
            ("translation", "en", "ta"),
            ("tts", "ta", None),
        ]:
            get_service_id(task, src, tgt)
        print("[✅ farm_advisory.router] Bhashini service IDs cached — voice ready")
    except Exception as e:
        print(f"[⚠️ farm_advisory.router] Prefetch failed (non-fatal): {e}")


# Run in background thread so startup doesn't block
threading.Thread(target=_startup_prefetch, daemon=True).start()

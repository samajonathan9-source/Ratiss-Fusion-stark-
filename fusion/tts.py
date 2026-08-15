"""fusion.tts — synthèse vocale OFFLINE.

gTTS (utilisé par robot-Ratiss-) nécessite internet (il interroge Google).
Pour un runtime 100% offline, on utilise pyttsx3 (moteur eSpeak-ng local).
gTTS reste disponible comme fallback optionnel si la qualité est privilégiée.

Ordre de préférence :
  1. pyttsx3 (offline, local, instantané)
  2. gTTS (online, qualité supérieure, fallback)
  3. désactivé (aucun moteur disponible)
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


class OfflineTTS:
    """Synthèse vocale offline avec fallback gracieux."""

    def __init__(self, prefer_gtts: bool = False, gtts_lang: str = "en",
                 pyttsx3_rate: int = 150):
        self.prefer_gtts = prefer_gtts
        self.gtts_lang = gtts_lang
        self.pyttsx3_rate = pyttsx3_rate
        self._pyttsx3 = None
        self._gtts_ok = None
        self._init_engines()

    def _init_engines(self):
        if not self.prefer_gtts:
            try:
                import pyttsx3
                self._pyttsx3 = pyttsx3.init()
                self._pyttsx3.setProperty("rate", self.pyttsx3_rate)
            except Exception:
                self._pyttsx3 = None

    def available(self) -> bool:
        return self._pyttsx3 is not None or self._gtts_available()

    def _gtts_available(self) -> bool:
        if self._gtts_ok is not None:
            return self._gtts_ok
        try:
            from gtts import gTTS  # noqa: F401
            self._gtts_ok = True
        except Exception:
            self._gtts_ok = False
        return self._gtts_ok

    def speak_to_file(self, text: str, out_path: str | Path | None = None) -> str | None:
        """Synthétise `text` vers un fichier audio. Retourne le chemin ou None."""
        if not text or not text.strip():
            return None
        out_path = str(out_path) if out_path else None
        # 1. pyttsx3 offline
        if self._pyttsx3 is not None and not self.prefer_gtts:
            try:
                path = out_path or tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False).name
                self._pyttsx3.save_to_file(text, path)
                self._pyttsx3.runAndWait()
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    return path
            except Exception:
                pass
        # 2. gTTS fallback (online)
        if self._gtts_available():
            try:
                from gtts import gTTS
                path = out_path or tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False).name
                gTTS(text=text, lang=self.gtts_lang).save(path)
                return path
            except Exception:
                pass
        return None

    def engine_name(self) -> str:
        if self._pyttsx3 is not None and not self.prefer_gtts:
            return "pyttsx3 (offline)"
        if self._gtts_available():
            return "gTTS (online fallback)"
        return "aucun (TTS désactivé)"

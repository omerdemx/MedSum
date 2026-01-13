"""
Konfigürasyon yönetimi modülü.
Environment variables'dan ayarları yükler.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API ayarları
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable must be set")

# Akademik arama API ayarları
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", None)  # Opsiyonel: https://www.semanticscholar.org/product/api

# API ayarları
API_TITLE = "MedInsight API"
API_DESCRIPTION = "Tıbbi literatür analiz platformu için backend API"
API_VERSION = "1.0.0"


"""
NLP işlemleri için servis modülü.
OpenAI API kullanarak çeviri, özet ve klinik çıkarım işlemlerini yönetir.
"""
from typing import List
import openai
from config import OPENAI_API_KEY

# OpenAI client'ı başlat
openai.api_key = OPENAI_API_KEY


async def translate_to_turkish(text: str) -> str:
    """
    İngilizce metni Türkçe'ye çevir (optimize edilmiş - token tasarrufu).
    """
    try:
        # Abstract'i kısalt (ilk 800 karakter) - token tasarrufu
        text_short = text[:800] + "..." if len(text) > 800 else text
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Daha hızlı ve ucuz model
            messages=[
                {
                    "role": "system",
                    "content": "Tıbbi çevirmen. Kısa, öz çeviri yap."
                },
                {
                    "role": "user",
                    "content": f"Çevir:\n{text_short}"
                }
            ],
            temperature=0.2,
            max_tokens=400  # Çıktıyı sınırla
        )
        
        translation = response.choices[0].message.content.strip()
        return translation
    
    except Exception as e:
        raise Exception(f"Çeviri hatası: {str(e)}")


async def generate_summary(abstract_en: str, abstract_tr: str) -> str:
    # abstract_en parametresi artık kullanılmıyor (token tasarrufu için)
    """
    Abstract'ten kısa bir Türkçe özet oluştur (optimize edilmiş).
    """
    try:
        # Sadece ilk 400 karakter kullan - token tasarrufu
        abstract_short = abstract_tr[:400] + "..." if len(abstract_tr) > 400 else abstract_tr
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Daha hızlı model
            messages=[
                {
                    "role": "system",
                    "content": "Kısa özet oluştur (2-3 cümle)."
                },
                {
                    "role": "user",
                    "content": f"Özet:\n{abstract_short}"
                }
            ],
            temperature=0.3,
            max_tokens=150  # Çıktıyı sınırla
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
    
    except Exception as e:
        raise Exception(f"Özet oluşturma hatası: {str(e)}")


async def extract_key_takeaways(abstract_en: str, abstract_tr: str, summary_tr: str) -> List[str]:
    # abstract_en ve abstract_tr parametreleri artık kullanılmıyor (token tasarrufu için)
    """
    Abstract'ten klinik önemli çıkarımları çıkar (optimize edilmiş).
    """
    try:
        # Sadece özeti kullan - token tasarrufu
        input_text = summary_tr[:300] if len(summary_tr) > 300 else summary_tr
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Daha hızlı model
            messages=[
                {
                    "role": "system",
                    "content": "3 kısa klinik çıkarım listele (her biri 1 cümle)."
                },
                {
                    "role": "user",
                    "content": f"Çıkarımlar:\n{input_text}"
                }
            ],
            temperature=0.4,
            max_tokens=200  # Çıktıyı sınırla
        )
        
        takeaways_text = response.choices[0].message.content.strip()
        
        # Metni madde işaretlerine göre ayır
        takeaways = []
        for line in takeaways_text.split('\n'):
            line = line.strip()
            if line:
                # Madde işaretlerini temizle
                for prefix in ['-', '*', '•', '1.', '2.', '3.', '4.', '5.']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                if line and len(line) > 15:  # Çok kısa olanları atla
                    takeaways.append(line)
        
        # 3 çıkarım sağla (5 yerine 3 - token tasarrufu)
        if len(takeaways) < 3:
            sentences = takeaways_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 20:
                    takeaways.append(sentence)
                    if len(takeaways) >= 3:
                        break
        
        # Minimum 3, maksimum 3 çıkarım
        while len(takeaways) < 3:
            takeaways.append("Bu çalışmanın sonuçları klinik pratikte dikkate alınmalıdır.")
        
        return takeaways[:3]  # Sadece 3 çıkarım
    
    except Exception as e:
        raise Exception(f"Çıkarım çıkarma hatası: {str(e)}")


async def translate_title(title_en: str) -> str:
    """
    Makale başlığını Türkçe'ye çevir (optimize edilmiş).
    """
    try:
        # Başlığı kısalt (100 karakter) - token tasarrufu
        title_short = title_en[:100] if len(title_en) > 100 else title_en
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Daha hızlı model
            messages=[
                {
                    "role": "system",
                    "content": "Tıbbi başlık çevir."
                },
                {
                    "role": "user",
                    "content": f"Çevir: {title_short}"
                }
            ],
            temperature=0.2,
            max_tokens=100  # Çıktıyı sınırla
        )
        
        title_tr = response.choices[0].message.content.strip()
        return title_tr
    
    except Exception as e:
        raise Exception(f"Başlık çeviri hatası: {str(e)}")


"""
MedInsight API - Ana FastAPI uygulaması.
Tıbbi literatür analiz platformu için backend API.
"""
import asyncio
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import API_TITLE, API_DESCRIPTION, API_VERSION
from models.schemas import AnalyzeArticlesRequest, ArticleResponse, ErrorResponse
from services.academic_search_service import search_all_sources
from services.nlp_service import (
    translate_to_turkish,
    translate_title,
    generate_summary,
    extract_key_takeaways
)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# CORS middleware ekle (gerekirse frontend entegrasyonu için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API kök endpoint'i - sağlık kontrolü."""
    return {
        "message": "MedInsight API çalışıyor",
        "version": API_VERSION,
        "endpoints": {
            "analyze_articles": "/api/analyze_articles"
        }
    }


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i."""
    return {"status": "healthy"}


@app.post(
    "/api/analyze_articles",
    response_model=List[ArticleResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Başarılı - İşlenmiş makale listesi döner"},
        500: {"model": ErrorResponse, "description": "Sunucu hatası"}
    }
)
async def analyze_articles(request: AnalyzeArticlesRequest):
    """
    PubMed'den makale arama, çeviri, özet ve klinik çıkarım işlemlerini gerçekleştir.
    
    Bu endpoint şu adımları izler:
    1. PubMed'den makale arama ve filtreleme
    2. Her makale için tam Türkçe çeviri
    3. Kısa Türkçe özet oluşturma (maksimum 4 cümle)
    4. Klinik önemli çıkarımları belirleme (3-5 adet)
    
    Args:
        request: AnalyzeArticlesRequest - keyword, article_count, time_range_years içerir
    
    Returns:
        List[ArticleResponse]: İşlenmiş makale listesi
    """
    try:
        # Step 1: Ücretsiz akademik kaynaklardan makaleleri çek
        articles_data = await search_all_sources(
            keyword=request.keyword,
            article_count=request.article_count,
            time_range_years=request.time_range_years
        )
        
        if not articles_data:
            return []
        
        # Her makale için NLP işlemlerini gerçekleştir
        processed_articles = []
        
        for article in articles_data:
            try:
                abstract_en = article.get("abstract_en", "")
                
                # Abstract boşsa atla
                if not abstract_en or len(abstract_en.strip()) < 50:
                    continue
                
                # Abstract'i kısalt (ilk 600 karakter) - token tasarrufu
                abstract_en = abstract_en[:600] + "..." if len(abstract_en) > 600 else abstract_en
                
                # Step 2: NLP işlemleri - paralel olarak çalıştırılabilir
                # Başlık çevirisi
                title_tr_task = translate_title(article.get("title_en", ""))
                
                # Abstract çevirisi
                abstract_tr_task = translate_to_turkish(abstract_en)
                
                # İlk iki işlemi bekle
                title_tr, abstract_tr = await asyncio.gather(
                    title_tr_task,
                    abstract_tr_task
                )
                
                # Özet ve çıkarımlar için abstract_tr'ye ihtiyaç var
                # Özet oluştur (sadece abstract_tr kullan - token tasarrufu)
                summary_tr = await generate_summary("", abstract_tr)  # abstract_en kullanma
                
                # Klinik çıkarımları çıkar (sadece summary_tr kullan - token tasarrufu)
                key_takeaways_tr = await extract_key_takeaways(
                    "",
                    "",
                    summary_tr
                )
                
                # Response objesi oluştur
                processed_article = ArticleResponse(
                    pmid=article.get("paper_id", ""),  # paper_id kullan (pmid yerine)
                    title_en=article.get("title_en", ""),
                    title_tr=title_tr,
                    authors=article.get("authors", []),
                    publication_date=article.get("publication_date", ""),
                    doi=article.get("doi"),
                    pubmed_url=article.get("url", ""),  # url kullan (pubmed_url yerine)
                    abstract_tr=abstract_tr,
                    summary_tr=summary_tr,
                    key_takeaways_tr=key_takeaways_tr
                )
                
                processed_articles.append(processed_article)
            
            except Exception as e:
                # Tek bir makale işlenirken hata oluşursa logla ve devam et
                print(f"Uyarı: Makale işlenirken hata oluştu (ID: {article.get('paper_id', 'bilinmeyen')}): {str(e)}")
                continue
        
        if not processed_articles:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Hiçbir makale başarıyla işlenemedi. Lütfen farklı bir anahtar kelime deneyin."
            )
        
        return processed_articles
    
    except HTTPException:
        # HTTPException'ları olduğu gibi fırlat
        raise
    
    except Exception as e:
        # Diğer hatalar için 500 döndür
        error_message = f"Makale analiz işlemi sırasında hata oluştu: {str(e)}"
        print(f"Hata: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


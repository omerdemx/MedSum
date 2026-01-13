"""
Pydantic şemaları - API request/response modelleri.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class AnalyzeArticlesRequest(BaseModel):
    """API isteği için şema."""
    keyword: str = Field(..., description="Aranacak anahtar kelime (arXiv, DOAJ, Europe PMC, Semantic Scholar)")
    article_count: int = Field(..., ge=1, le=50, description="Alınacak makale sayısı (1-50 arası)")
    time_range_years: Optional[int] = Field(None, ge=1, le=20, description="Son N yıl içindeki makaleler (opsiyonel)")


class ArticleResponse(BaseModel):
    """İşlenmiş makale için response şeması."""
    pmid: str = Field(..., description="Makale ID (PMID veya diğer kaynak ID'leri)")
    title_en: str = Field(..., description="İngilizce başlık")
    title_tr: str = Field(..., description="Türkçe başlık")
    authors: List[str] = Field(..., description="Yazar listesi")
    publication_date: str = Field(..., description="Yayın tarihi (YYYY-MM-DD)")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    pubmed_url: str = Field(..., description="Makale URL'i (PubMed veya diğer kaynaklar)")
    abstract_tr: str = Field(..., description="Türkçe tam çeviri")
    summary_tr: str = Field(..., description="Türkçe kısa özet (maksimum 4 cümle)")
    key_takeaways_tr: List[str] = Field(..., min_length=3, max_length=3, description="Klinik önemli çıkarımlar (3 adet)")


class ErrorResponse(BaseModel):
    """Hata yanıtı için şema."""
    error: str = Field(..., description="Hata mesajı")
    detail: Optional[str] = Field(None, description="Detaylı hata açıklaması")


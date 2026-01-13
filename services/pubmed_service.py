"""
PubMed API entegrasyonu için servis modülü.
BioPython.Entrez kullanarak makale arama ve veri çekme işlemlerini yönetir.
"""
import time
import io
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from Bio import Entrez
from config import PUBMED_EMAIL


# Entrez email ayarını yap
Entrez.email = PUBMED_EMAIL


async def search_pubmed(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[str]:
    """
    PubMed'de anahtar kelime ile makale arama.
    
    Args:
        keyword: Aranacak anahtar kelime
        article_count: Alınacak makale sayısı
        time_range_years: Son N yıl içindeki makaleler (opsiyonel)
    
    Returns:
        PubMed ID listesi
    """
    try:
        # Tarih filtresi oluştur
        search_query = keyword
        if time_range_years:
            # Son N yıl içindeki makaleler için tarih filtresi ekle
            # PubMed'de reldate parametresi kullanılabilir (gün cinsinden)
            days_ago = time_range_years * 365
            # Alternatif olarak tarih aralığı kullan
            cutoff_date = datetime.now() - timedelta(days=days_ago)
            date_str = cutoff_date.strftime("%Y/%m/%d")
            current_date_str = datetime.now().strftime("%Y/%m/%d")
            search_query = f"{keyword} AND ({date_str}[PDAT] : {current_date_str}[PDAT])"
        
        # PubMed'de arama yap
        handle = Entrez.esearch(
            db="pubmed",
            term=search_query,
            retmax=article_count,
            sort="relevance"
        )
        search_results = Entrez.read(handle)
        handle.close()
        
        # Rate limiting için kısa bekleme
        time.sleep(0.3)
        
        pmids = search_results["IdList"]
        return pmids
    
    except Exception as e:
        raise Exception(f"PubMed arama hatası: {str(e)}")


async def fetch_article_details(pmid: str) -> Dict[str, Optional[str]]:
    """
    Belirli bir PubMed ID için detaylı makale bilgilerini çek.
    
    Args:
        pmid: PubMed ID
    
    Returns:
        Makale detaylarını içeren dictionary
    """
    try:
        # Makale detaylarını çek
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="xml")
        
        # XML'i parse et - handle doğrudan Entrez.read() ile kullanılabilir
        records = Entrez.read(handle)
        handle.close()
        
        # Rate limiting
        time.sleep(0.3)
        
        # İlk makaleyi al (genellikle tek makale döner)
        if "PubmedArticle" not in records or not records["PubmedArticle"]:
            raise Exception(f"PMID {pmid} için makale bulunamadı")
        
        article = records["PubmedArticle"][0]
        medline_citation = article["MedlineCitation"]
        pubmed_data = article.get("PubmedData", {})
        
        # Başlık çıkar
        article_data = medline_citation.get("Article", {})
        title_en = article_data.get("ArticleTitle", "")
        
        # Yazar listesi çıkar
        authors = []
        author_list = article_data.get("AuthorList", [])
        for author in author_list:
            last_name = author.get("LastName", "")
            first_name = author.get("ForeName", "")
            initials = author.get("Initials", "")
            if last_name:
                author_name = f"{last_name} {initials}".strip()
                authors.append(author_name)
        
        # Yayın tarihi çıkar
        pub_date = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        year = pub_date.get("Year", "")
        month = pub_date.get("Month", "01")
        day = pub_date.get("Day", "01")
        
        # Ay ve gün formatını düzelt
        if not month or month == "":
            month = "01"
        if len(month) == 1:
            month = f"0{month}"
        if not day or day == "":
            day = "01"
        if len(day) == 1:
            day = f"0{day}"
        
        publication_date = f"{year}-{month}-{day}" if year else None
        
        # Abstract çıkar
        abstract_en = ""
        abstract_data = article_data.get("Abstract", {})
        if abstract_data:
            abstract_list = abstract_data.get("AbstractText", [])
            if isinstance(abstract_list, list):
                # Birden fazla abstract paragrafı varsa birleştir
                abstract_parts = []
                for abstract_item in abstract_list:
                    if isinstance(abstract_item, dict):
                        # Label ve text içeren dict yapısı
                        text = abstract_item.get("text", abstract_item.get("#text", str(abstract_item)))
                        if text:
                            abstract_parts.append(str(text))
                    else:
                        abstract_parts.append(str(abstract_item))
                abstract_en = " ".join(abstract_parts)
            elif isinstance(abstract_list, str):
                abstract_en = abstract_list
        
        # DOI çıkar
        doi = None
        if pubmed_data:
            article_id_list = pubmed_data.get("ArticleIdList", [])
            if article_id_list:
                for article_id in article_id_list:
                    # BioPython'de ArticleId bir dict veya özel obje olabilir
                    if isinstance(article_id, dict):
                        if article_id.get("attributes", {}).get("IdType") == "doi":
                            doi = str(article_id.get("#text", article_id))
                            break
                    elif hasattr(article_id, 'attributes'):
                        if article_id.attributes.get("IdType") == "doi":
                            doi = str(article_id)
                            break
                    # String olarak da gelebilir
                    elif isinstance(article_id, str) and "doi" in str(article_id).lower():
                        doi = str(article_id)
                        break
        
        # PubMed URL oluştur
        pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        
        return {
            "pmid": pmid,
            "title_en": title_en,
            "authors": authors,
            "publication_date": publication_date,
            "abstract_en": abstract_en,
            "doi": doi,
            "pubmed_url": pubmed_url
        }
    
    except Exception as e:
        raise Exception(f"PMID {pmid} için makale detayları çekilirken hata: {str(e)}")


async def fetch_articles(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[Dict[str, Optional[str]]]:
    """
    PubMed'den makale arama ve detaylarını çekme ana fonksiyonu.
    
    Args:
        keyword: Aranacak anahtar kelime
        article_count: Alınacak makale sayısı
        time_range_years: Son N yıl içindeki makaleler (opsiyonel)
    
    Returns:
        Makale detaylarını içeren dictionary listesi
    """
    # PubMed ID'leri bul
    pmids = await search_pubmed(keyword, article_count, time_range_years)
    
    if not pmids:
        return []
    
    # Her makale için detayları çek
    articles = []
    for pmid in pmids:
        try:
            article_details = await fetch_article_details(pmid)
            # Abstract boşsa atla
            if article_details.get("abstract_en"):
                articles.append(article_details)
        except Exception as e:
            # Hata durumunda logla ve devam et
            print(f"Uyarı: {str(e)}")
            continue
    
    return articles


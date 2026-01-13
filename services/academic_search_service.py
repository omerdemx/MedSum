"""
Ücretsiz akademik makale arama servisi.
Semantic Scholar, arXiv, DOAJ ve Europe PMC API'lerini kullanır.
"""
import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta


# Semantic Scholar API - Ücretsiz, API key gerektiriyor (kolay alınıyor)
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
try:
    from config import SEMANTIC_SCHOLAR_API_KEY
except ImportError:
    SEMANTIC_SCHOLAR_API_KEY = None

# arXiv API - Tamamen ücretsiz, API key gerektirmiyor
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# DOAJ API - Ücretsiz, API key gerektirmiyor
DOAJ_API_URL = "https://doaj.org/api/v2/search/articles"

# Europe PMC API - Ücretsiz, API key gerektirmiyor
EUROPE_PMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


async def search_semantic_scholar(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[Dict]:
    """
    Semantic Scholar API ile makale arama.
    API key: https://www.semanticscholar.org/product/api adresinden alınabilir (ücretsiz)
    """
    try:
        headers = {}
        # Semantic Scholar API key opsiyonel (ücretsiz tier için gerekli değil)
        try:
            from config import SEMANTIC_SCHOLAR_API_KEY as api_key
            if api_key:
                headers["x-api-key"] = api_key
        except (ImportError, AttributeError):
            pass
        
        # Tarih filtresi
        year_filter = ""
        if time_range_years:
            year = datetime.now().year - time_range_years
            year_filter = f",year:>={year}"
        
        params = {
            "query": keyword,
            "limit": min(article_count, 100),
            "fields": "title,authors,year,abstract,url,doi,venue,publicationDate"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                SEMANTIC_SCHOLAR_API_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for paper in data.get("data", [])[:article_count]:
                abstract = paper.get("abstract", "")
                if abstract:
                    # Abstract'i kısalt (ilk 600 karakter) - token tasarrufu
                    abstract_short = abstract[:600] + "..." if len(abstract) > 600 else abstract
                    articles.append({
                        "source": "semantic_scholar",
                        "title_en": paper.get("title", ""),
                        "authors": [f"{author.get('name', '')}" for author in paper.get("authors", [])[:5]],  # İlk 5 yazar
                        "publication_date": paper.get("publicationDate") or f"{paper.get('year', '')}-01-01",
                        "abstract_en": abstract_short,
                        "doi": paper.get("doi"),
                        "url": paper.get("url") or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                        "venue": paper.get("venue", ""),
                        "paper_id": paper.get("paperId", "")
                    })
            
            return articles
    
    except Exception as e:
        print(f"Semantic Scholar arama hatası: {str(e)}")
        return []


async def search_arxiv(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[Dict]:
    """
    arXiv API ile makale arama.
    Tamamen ücretsiz, API key gerektirmiyor.
    """
    try:
        # arXiv arama sorgusu
        search_query = f'all:{keyword}'
        
        # Tarih filtresi
        if time_range_years:
            year = datetime.now().year - time_range_years
            search_query += f" AND submittedDate:[{year}0101* TO {datetime.now().strftime('%Y%m%d')}]"
        
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(article_count, 100),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(ARXIV_API_URL, params=params)
            response.raise_for_status()
            
            # XML parse et
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            articles = []
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace)[:article_count]:
                title = entry.find('atom:title', namespace)
                summary = entry.find('atom:summary', namespace)
                published = entry.find('atom:published', namespace)
                authors = entry.findall('atom:author', namespace)
                link = entry.find('atom:id', namespace)
                
                if summary is not None and summary.text:
                    author_list = [author.find('atom:name', namespace).text for author in authors[:5] if author.find('atom:name', namespace) is not None]  # İlk 5 yazar
                    abstract_text = summary.text.strip()
                    # Abstract'i kısalt (600 karakter) - token tasarrufu
                    abstract_short = abstract_text[:600] + "..." if len(abstract_text) > 600 else abstract_text
                    
                    articles.append({
                        "source": "arxiv",
                        "title_en": title.text if title is not None else "",
                        "authors": author_list,
                        "publication_date": published.text[:10] if published is not None else "",
                        "abstract_en": abstract_short,
                        "doi": None,
                        "url": link.text if link is not None else "",
                        "venue": "arXiv",
                        "paper_id": entry.find('atom:id', namespace).text.split('/')[-1] if entry.find('atom:id', namespace) is not None else ""
                    })
            
            return articles
    
    except Exception as e:
        print(f"arXiv arama hatası: {str(e)}")
        return []


async def search_europe_pmc(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[Dict]:
    """
    Europe PMC API ile makale arama.
    Ücretsiz, API key gerektirmiyor.
    """
    try:
        # Tarih filtresi
        date_filter = ""
        if time_range_years:
            year = datetime.now().year - time_range_years
            date_filter = f" AND PUB_YEAR:[{year} TO {datetime.now().year}]"
        
        params = {
            "query": f"{keyword}{date_filter}",
            "resultType": "core",
            "pageSize": min(article_count, 100),
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(EUROPE_PMC_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for result in data.get("resultList", {}).get("result", [])[:article_count]:
                abstract_text = result.get("abstractText", "")
                if abstract_text:
                    authors = []
                    if result.get("authorList", {}).get("author"):
                        for author in result["authorList"]["author"][:5]:  # İlk 5 yazar
                            name = f"{author.get('firstName', '')} {author.get('lastName', '')}".strip()
                            if name:
                                authors.append(name)
                    
                    # Abstract'i kısalt (600 karakter) - token tasarrufu
                    abstract_short = abstract_text[:600] + "..." if len(abstract_text) > 600 else abstract_text
                    
                    articles.append({
                        "source": "europe_pmc",
                        "title_en": result.get("title", ""),
                        "authors": authors,
                        "publication_date": result.get("firstPublicationDate", "")[:10] if result.get("firstPublicationDate") else "",
                        "abstract_en": abstract_short,
                        "doi": result.get("doi"),
                        "url": f"https://europepmc.org/article/MED/{result.get('pmid', '')}" if result.get("pmid") else result.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", ""),
                        "venue": result.get("journalTitle", ""),
                        "paper_id": result.get("pmid") or result.get("id", "")
                    })
            
            return articles
    
    except Exception as e:
        print(f"Europe PMC arama hatası: {str(e)}")
        return []


async def search_doaj(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None
) -> List[Dict]:
    """
    DOAJ (Directory of Open Access Journals) API ile makale arama.
    Ücretsiz, API key gerektirmiyor.
    """
    try:
        # Tarih filtresi
        date_filter = ""
        if time_range_years:
            year = datetime.now().year - time_range_years
            date_filter = f" AND year:[{year} TO {datetime.now().year}]"
        
        params = {
            "q": f"{keyword}{date_filter}",
            "pageSize": min(article_count, 100)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(DOAJ_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for result in data.get("results", [])[:article_count]:
                abstract_text = result.get("bibjson", {}).get("abstract", "")
                if abstract_text:
                    authors = []
                    if result.get("bibjson", {}).get("author"):
                        for author in result["bibjson"]["author"][:5]:  # İlk 5 yazar
                            if isinstance(author, dict):
                                name = author.get("name", "")
                            else:
                                name = str(author)
                            if name:
                                authors.append(name)
                    
                    # Abstract'i kısalt (600 karakter) - token tasarrufu
                    abstract_short = abstract_text[:600] + "..." if len(abstract_text) > 600 else abstract_text
                    
                    articles.append({
                        "source": "doaj",
                        "title_en": result.get("bibjson", {}).get("title", ""),
                        "authors": authors,
                        "publication_date": result.get("bibjson", {}).get("year", "") + "-01-01" if result.get("bibjson", {}).get("year") else "",
                        "abstract_en": abstract_short,
                        "doi": result.get("bibjson", {}).get("identifier", [{}])[0].get("id") if result.get("bibjson", {}).get("identifier") else None,
                        "url": result.get("bibjson", {}).get("link", [{}])[0].get("url", "") if result.get("bibjson", {}).get("link") else "",
                        "venue": result.get("bibjson", {}).get("journal", {}).get("title", ""),
                        "paper_id": result.get("id", "")
                    })
            
            return articles
    
    except Exception as e:
        print(f"DOAJ arama hatası: {str(e)}")
        return []


async def search_all_sources(
    keyword: str,
    article_count: int,
    time_range_years: Optional[int] = None,
    sources: Optional[List[str]] = None
) -> List[Dict]:
    """
    Tüm kaynaklardan paralel olarak makale arama.
    
    Args:
        keyword: Aranacak anahtar kelime
        article_count: Toplam alınacak makale sayısı
        time_range_years: Son N yıl içindeki makaleler
        sources: Kullanılacak kaynaklar listesi (None ise hepsi kullanılır)
    
    Returns:
        Makale listesi
    """
    if sources is None:
        sources = ["arxiv", "europe_pmc", "doaj"]  # Semantic Scholar varsayılan olarak kapalı (API key gerektiriyor)
    
    tasks = []
    
    if "semantic_scholar" in sources:
        tasks.append(search_semantic_scholar(keyword, article_count, time_range_years))
    if "arxiv" in sources:
        tasks.append(search_arxiv(keyword, article_count, time_range_years))
    if "europe_pmc" in sources:
        tasks.append(search_europe_pmc(keyword, article_count, time_range_years))
    if "doaj" in sources:
        tasks.append(search_doaj(keyword, article_count, time_range_years))
    
    if not tasks:
        return []
    
    # Paralel olarak tüm kaynaklardan ara
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Tüm sonuçları birleştir
    all_articles = []
    for result in results:
        if isinstance(result, list):
            all_articles.extend(result)
        elif isinstance(result, Exception):
            print(f"Arama hatası: {str(result)}")
    
    # Duplicate'leri kaldır (DOI veya URL'ye göre)
    seen = set()
    unique_articles = []
    for article in all_articles:
        identifier = article.get("doi") or article.get("url") or article.get("paper_id")
        if identifier and identifier not in seen:
            seen.add(identifier)
            unique_articles.append(article)
        elif not identifier:
            unique_articles.append(article)
    
    # İstenen sayıya kadar sınırla
    return unique_articles[:article_count]


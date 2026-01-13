import { useState } from 'react';

function ArticleCard({ article }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="article-card">
      {/* Header */}
      <div className="article-section">
        <h2 className="article-title">
          {article.title_tr || article.title_en}
        </h2>
        {article.title_en && article.title_en !== article.title_tr && (
          <p className="article-title-en">{article.title_en}</p>
        )}
      </div>

      {/* Metadata */}
      <div className="article-meta">
        <div>
          <span>Yazarlar: </span>
          {article.authors?.join(', ') || 'Bilinmiyor'}
        </div>
        <div>
          <span>Yayın Tarihi: </span>
          {article.publication_date || 'Bilinmiyor'}
        </div>
        {article.doi && (
          <div>
            <span>DOI: </span>
            <span style={{ color: '#4f46e5' }}>{article.doi}</span>
          </div>
        )}
        <div>
          <span>ID: </span>
          <a
            href={article.pubmed_url}
            target="_blank"
            rel="noopener noreferrer"
            className="article-link"
          >
            {article.pmid}
          </a>
        </div>
      </div>

      {/* Summary */}
      <div className="article-section">
        <h3>Özet</h3>
        <p>{article.summary_tr}</p>
      </div>

      {/* Key Takeaways */}
      <div className="article-section">
        <h3>Klinik Önemli Çıkarımlar</h3>
        <ul className="article-list">
          {article.key_takeaways_tr?.map((takeaway, index) => (
            <li key={index}>{takeaway}</li>
          ))}
        </ul>
      </div>

      {/* Expandable Abstract */}
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '1rem' }}>
        <button
          onClick={() => setExpanded(!expanded)}
          className="expand-btn"
        >
          {expanded ? 'Özeti Gizle' : 'Tam Çeviriyi Görüntüle'}
          <svg
            style={{
              marginLeft: '0.5rem',
              width: '1rem',
              height: '1rem',
              transform: expanded ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.2s'
            }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {expanded && (
          <div className="expanded-content">
            {article.abstract_tr}
          </div>
        )}
      </div>

      {/* External Link */}
      <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb' }}>
        <a
          href={article.pubmed_url}
          target="_blank"
          rel="noopener noreferrer"
          className="article-link"
          style={{ display: 'inline-flex', alignItems: 'center', fontWeight: '500' }}
        >
          Görüntüle
          <svg style={{ marginLeft: '0.5rem', width: '1rem', height: '1rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  );
}

export default ArticleCard;

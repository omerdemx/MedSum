import { useState } from 'react';

function SearchForm({ onSearch, disabled }) {
  const [keyword, setKeyword] = useState('');
  const [articleCount, setArticleCount] = useState(5);
  const [timeRangeYears, setTimeRangeYears] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (keyword.trim()) {
      onSearch(keyword.trim(), articleCount, timeRangeYears ? parseInt(timeRangeYears) : null);
    }
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="keyword">Anahtar Kelime</label>
          <input
            type="text"
            id="keyword"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Örn: diabetic retinopathy treatment"
            required
            disabled={disabled}
          />
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="articleCount">Makale Sayısı (1-50)</label>
            <input
              type="number"
              id="articleCount"
              value={articleCount}
              onChange={(e) => setArticleCount(Math.min(50, Math.max(1, parseInt(e.target.value) || 1)))}
              min="1"
              max="50"
              required
              disabled={disabled}
            />
          </div>

          <div className="form-group">
            <label htmlFor="timeRangeYears">Son N Yıl (Opsiyonel)</label>
            <input
              type="number"
              id="timeRangeYears"
              value={timeRangeYears}
              onChange={(e) => setTimeRangeYears(e.target.value)}
              placeholder="Örn: 5"
              min="1"
              max="20"
              disabled={disabled}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn"
          disabled={disabled || !keyword.trim()}
        >
          {disabled ? 'Aranıyor...' : 'Makale Ara'}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;

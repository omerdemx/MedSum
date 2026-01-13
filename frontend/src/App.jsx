import { useState } from 'react';
import { analyzeArticles } from './services/api';
import SearchForm from './components/SearchForm';
import ArticleList from './components/ArticleList';
import LoadingSpinner from './components/LoadingSpinner';
import './index.css';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (keyword, articleCount, timeRangeYears) => {
    setLoading(true);
    setError(null);
    setArticles([]);

    try {
      const results = await analyzeArticles(keyword, articleCount, timeRangeYears);
      setArticles(results);
    } catch (err) {
      const errorMessage = err?.detail || err?.error || err?.message || 'Bir hata oluştu. Lütfen tekrar deneyin.';
      setError(errorMessage);
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1>MedInsight</h1>
          <p>Tıbbi Literatür Analiz Platformu</p>
        </header>

        {/* Search Form */}
        <div className="form-container">
          <SearchForm onSearch={handleSearch} disabled={loading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-box">
            <p style={{ fontWeight: '600' }}>Hata:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="form-container">
            <LoadingSpinner />
          </div>
        )}

        {/* Results */}
        {!loading && articles.length > 0 && (
          <div className="results-container">
            <div className="results-count">
              {articles.length} makale bulundu
            </div>
            <ArticleList articles={articles} />
          </div>
        )}

        {/* No Results */}
        {!loading && articles.length === 0 && !error && (
          <div className="empty-state">
            <p>Makale aramak için yukarıdaki formu kullanın.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

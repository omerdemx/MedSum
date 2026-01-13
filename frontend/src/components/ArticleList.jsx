import ArticleCard from './ArticleCard';

function ArticleList({ articles }) {
  return (
    <div className="space-y-6">
      {articles.map((article, index) => (
        <ArticleCard key={article.pmid || index} article={article} />
      ))}
    </div>
  );
}

export default ArticleList;



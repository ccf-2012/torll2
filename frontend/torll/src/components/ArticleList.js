import React from 'react';

function ArticleList({ articles }) {
  return (
    <div className="article-list">
      <h2>Articles</h2>
      <ul>
        {articles.map(article => (
          <li key={article.id}>
            <a href={article.info_link} target="_blank" rel="noopener noreferrer">
              {article.title}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ArticleList;
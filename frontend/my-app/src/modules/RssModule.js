import React, { useState, useEffect } from 'react';
import AddFeed from '../components/AddFeed';
import ArticleList from '../components/ArticleList';
import '../App.css';
import { useNotification } from '../contexts/NotificationContext';

function RssModule() {
  const [feeds, setFeeds] = useState([]);
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [articles, setArticles] = useState([]);
  const { showNotification } = useNotification();

  useEffect(() => {
    fetch('http://localhost:8000/rss/configs/')
      .then(response => response.json())
      .then(data => setFeeds(data))
      .catch(error => {
        console.error('Error fetching feeds:', error);
        showNotification('Error fetching feeds', 'error');
      });
  }, []);

  const addFeed = (feed) => {
    fetch('http://localhost:8000/rss/configs/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: feed.title, url: feed.url, site: 'unknown' }),
    })
      .then(response => response.json())
      .then(newFeed => {
        setFeeds([...feeds, newFeed]);
        showNotification('Feed added successfully', 'success');
      })
      .catch(error => {
        console.error('Error adding feed:', error);
        showNotification('Error adding feed', 'error');
      });
  };

  const selectFeed = (feed) => {
    setSelectedFeed(feed);
    setArticles([]); // Clear previous articles

    fetch(`http://localhost:8000/rss/process/${feed.name}`, { method: 'POST' })
      .then(() => {
        showNotification('Feed processing initiated', 'info');
        fetch(`http://localhost:8000/rss/history/${feed.name}`)
          .then(response => response.json())
          .then(data => {
            setArticles(data);
            showNotification('Articles fetched successfully', 'success');
          })
          .catch(error => {
            console.error('Error fetching articles:', error);
            showNotification('Error fetching articles', 'error');
          });
      })
      .catch(error => {
        console.error('Error processing feed:', error);
        showNotification('Error processing feed', 'error');
      });
  };

  return (
    <div>
      <header>
        <h1>RSS Reader</h1>
        <AddFeed onAddFeed={addFeed} />
      </header>
      <main className="App-main">
        <div className="feed-list">
          <h2>Feeds</h2>
          <ul>
            {feeds.map(feed => (
              <li key={feed.id} onClick={() => selectFeed(feed)}>
                {feed.name}
              </li>
            ))}
          </ul>
        </div>
        <ArticleList articles={articles} />
      </main>
    </div>
  );
}

export default RssModule;
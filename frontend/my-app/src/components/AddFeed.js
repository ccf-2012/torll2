import React, { useState } from 'react';

function AddFeed({ onAddFeed }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url) return;
    onAddFeed({ title: url, url });
    setUrl('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter RSS feed URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button type="submit">Add Feed</button>
    </form>
  );
}

export default AddFeed;

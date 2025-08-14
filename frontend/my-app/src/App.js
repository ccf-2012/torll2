import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import RssModule from './modules/RssModule';
import SiteTorrentsModule from './modules/SiteTorrentsModule';
import DownloadsModule from './modules/DownloadsModule';
import MediaLibraryModule from './modules/MediaLibraryModule';
import SearchModule from './modules/SearchModule';
import PtConfigModule from './modules/PtConfigModule'; // New import

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<RssModule />} />
          <Route path="/site-torrents" element={<SiteTorrentsModule />} />
          <Route path="/downloads" element={<DownloadsModule />} />
          <Route path="/media-library" element={<MediaLibraryModule />} />
          <Route path="/search" element={<SearchModule />} />
          <Route path="/pt-configs" element={<PtConfigModule />} /> {/* New route */}
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
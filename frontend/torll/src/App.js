import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import RssModule from './modules/RssModule';
import SiteTorrentsModule from './modules/SiteTorrentsModule';
import DownloadsModule from './modules/DownloadsModule';
import MediaLibraryModule from './modules/MediaLibraryModule';
import SearchModule from './modules/SearchModule';
import PtConfigModule from './modules/PtConfigModule';

function App() {
  const [mode, setMode] = useState('light');

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                primary: { main: '#556cd6' },
                secondary: { main: '#19857b' },
                background: { default: '#f4f6f8', paper: '#fff' },
              }
            : {
                primary: { main: '#90caf9' },
                secondary: { main: '#81c784' },
                background: { default: '#121212', paper: '#1e1e1e' },
              }),
        },
      }),
    [mode],
  );

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [],
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout colorMode={colorMode} mode={mode}>
          <Routes>
            <Route path="/" element={<RssModule />} />
            <Route path="/site-torrents" element={<SiteTorrentsModule />} />
            <Route path="/downloads" element={<DownloadsModule />} />
            <Route path="/media-library" element={<MediaLibraryModule />} />
            <Route path="/search" element={<SearchModule />} />
            <Route path="/pt-configs" element={<PtConfigModule />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
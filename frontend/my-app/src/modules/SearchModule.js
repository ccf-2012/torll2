import React, { useState, useEffect } from 'react';
import { TextField, Button, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';

function SearchModule() {
  const [searchTerm, setSearchTerm] = useState('');
  const [siteName, setSiteName] = useState('default_site'); // Placeholder for site selection
  const [searchResults, setSearchResults] = useState([]);
  const [filterTitle, setFilterTitle] = useState(''); // New state for filtering
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchSearchResults();
  }, [filterTitle]); // Add filterTitle to dependencies

  const fetchSearchResults = () => {
    let url = 'http://localhost:8000/search/cache';
    if (filterTitle) {
      url += `?title=${filterTitle}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setSearchResults(data))
      .catch(error => {
        console.error('Error fetching search results:', error);
        showNotification('Error fetching search results', 'error');
      });
  };

  const handleSearch = () => {
    fetch('http://localhost:8000/search/pt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        search_term: searchTerm,
        site_name: siteName,
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Search initiated:', data);
        showNotification('Search initiated', 'info');
        // After initiating search, re-fetch from cache to see new results
        fetchSearchResults();
      })
      .catch(error => {
        console.error('Error initiating search:', error);
        showNotification('Error initiating search', 'error');
      });
  };

  const handleFilterTitleChange = (event) => {
    setFilterTitle(event.target.value);
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        PT Site Search
      </Typography>
      <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', mb: 2 }}>
        <TextField
          label="Search Term"
          variant="outlined"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <Button variant="contained" onClick={handleSearch} sx={{ ml: 2 }}>
          Search
        </Button>
      </Paper>
      <TextField
        label="Filter by Title"
        variant="outlined"
        fullWidth
        margin="normal"
        value={filterTitle}
        onChange={handleFilterTitleChange}
      />
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell align="right">Site</TableCell>
              <TableCell align="right">Size</TableCell>
              <TableCell align="right">Seeders</TableCell>
              <TableCell align="right">Leechers</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {searchResults.map((result) => (
              <TableRow
                key={result.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {result.tortitle}
                </TableCell>
                <TableCell align="right">{result.site}</TableCell>
                <TableCell align="right">{result.torsizestr}</TableCell>
                <TableCell align="right">{result.seednum}</TableCell>
                <TableCell align="right">{result.downnum}</TableCell>
                <TableCell align="right">
                  <Button variant="contained" onClick={() => console.log('Download:', result)}>
                    Download
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

export default SearchModule;
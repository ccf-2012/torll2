import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, IconButton,
  Box, Typography, Dialog, DialogActions, DialogContent, DialogTitle, TextField
} from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
} from '@tanstack/react-table';
import DeleteIcon from '@mui/icons-material/Delete';
import PageviewIcon from '@mui/icons-material/Pageview';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

function RssModule() {
  const [view, setView] = useState('feeds'); // 'feeds' or 'articles'
  const [feeds, setFeeds] = useState([]);
  const [articles, setArticles] = useState([]);
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [newFeedName, setNewFeedName] = useState('');
  const [newFeedUrl, setNewFeedUrl] = useState('');
  const { showNotification } = useNotification();

  const fetchFeeds = () => {
    fetch('/rss/configs/')
      .then(response => response.json())
      .then(data => setFeeds(data))
      .catch(error => {
        console.error('Error fetching feeds:', error);
        showNotification('Error fetching feeds', 'error');
      });
  };

  useEffect(() => {
    fetchFeeds();
  }, []);

  const handleAddFeed = () => {
    fetch('/rss/configs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newFeedName, rssUrl: newFeedUrl, site: 'default' }),
    })
      .then(response => response.json())
      .then(newFeed => {
        setFeeds([...feeds, newFeed]);
        showNotification('Feed added successfully', 'success');
        setOpenAddDialog(false);
        setNewFeedName('');
        setNewFeedUrl('');
      })
      .catch(error => {
        console.error('Error adding feed:', error);
        showNotification('Error adding feed', 'error');
      });
  };

  const handleDeleteFeed = (feedId) => {
    fetch(`/rss/configs/${feedId}`, { method: 'DELETE' })
      .then(() => {
        showNotification('Feed deleted successfully', 'success');
        fetchFeeds();
      })
      .catch(error => {
        console.error('Error deleting feed:', error);
        showNotification('Error deleting feed', 'error');
      });
  };

  const handleSelectFeed = (feed) => {
    setSelectedFeed(feed);
    setArticles([]);
    showNotification(`Processing ${feed.name}...`, 'info');
    fetch(`/rss/process/${feed.name}`, { method: 'POST' })
      .then(() => {
        fetch(`/rss/history/${feed.name}`)
          .then(response => response.json())
          .then(data => {
            setArticles(data);
            setView('articles'); // Switch view after fetching
          })
          .catch(error => showNotification('Error fetching articles', 'error'));
      })
      .catch(error => showNotification('Error processing feed', 'error'));
  };

  const columns = useMemo(() => {
    if (view === 'feeds') {
      return [
        { accessorKey: 'name', header: 'Feed Name' },
        {
          id: 'actions',
          header: 'Actions',
          cell: ({ row }) => (
            <Box>
              <IconButton size="small" onClick={() => handleSelectFeed(row.original)}>
                <PageviewIcon />
              </IconButton>
              <IconButton size="small" onClick={() => handleDeleteFeed(row.original.id)}>
                <DeleteIcon />
              </IconButton>
            </Box>
          ),
        },
      ];
    }
    // 'articles' view
    return [
      {
        accessorKey: 'title',
        header: 'Article Title',
        cell: ({ row }) => (
          <a href={row.original.info_link} target="_blank" rel="noopener noreferrer">
            {row.original.title}
          </a>
        ),
      },
      { accessorKey: 'pubdate', header: 'Published', cell: info => new Date(info.getValue()).toLocaleString() },
    ];
  }, [view]);

  const data = useMemo(() => (view === 'feeds' ? feeds : articles), [view, feeds, articles]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <Paper sx={{ p: { xs: 1, md: 2 }, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        {view === 'articles' && (
          <Button startIcon={<ArrowBackIcon />} onClick={() => setView('feeds')}>
            Back to Feeds
          </Button>
        )}
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {view === 'feeds' ? 'RSS Feeds' : `Articles from ${selectedFeed?.name}`}
        </Typography>
        {view === 'feeds' && (
          <Button variant="contained" onClick={() => setOpenAddDialog(true)}>Add Feed</Button>
        )}
      </Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <TableCell key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody>
            {table.getRowModel().rows.map(row => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map(cell => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>Add New RSS Feed</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" label="Feed Name" type="text" fullWidth variant="standard" value={newFeedName} onChange={(e) => setNewFeedName(e.target.value)} />
          <TextField margin="dense" label="Feed URL" type="text" fullWidth variant="standard" value={newFeedUrl} onChange={(e) => setNewFeedUrl(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button onClick={handleAddFeed}>Add</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

export default RssModule;
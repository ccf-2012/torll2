import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TextField, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Autocomplete, TableSortLabel, TablePagination } from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';

function MediaLibraryModule() {
  const [mediaItems, setMediaItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [open, setOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [tmdbId, setTmdbId] = useState('');
  const [tmdbCat, setTmdbCat] = useState('');
  const [tmdbSearchResults, setTmdbSearchResults] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('id');
  const [order, setOrder] = useState('asc'); // 'asc' or 'desc'
  const [filterTitle, setFilterTitle] = useState(''); // New state for filtering
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchMediaItems();
  }, [page, rowsPerPage, orderBy, order, filterTitle]); // Add filterTitle to dependencies

  const fetchMediaItems = () => {
    const skip = page * rowsPerPage;
    const limit = rowsPerPage;
    let url = `http://localhost:8000/media_items/?skip=${skip}&limit=${limit}&sort_by=${orderBy}&sort_order=${order}`;
    if (filterTitle) {
      url += `&title=${filterTitle}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setMediaItems(data))
      .catch(error => {
        console.error('Error fetching media items:', error);
        showNotification('Error fetching media items', 'error');
      });
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleClickOpen = (item) => {
    setSelectedItem(item);
    setTmdbId(item.tmdbid || '');
    setTmdbCat(item.tmdbcat || '');
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setTmdbSearchResults([]); // Clear search results on close
  };

  const handleTmdbSearch = (event, value) => {
    if (value && value.length > 2) { // Search only if more than 2 characters
      fetch(`http://localhost:8000/tmdb/search?query=${value}`)
        .then(response => response.json())
        .then(data => setTmdbSearchResults(data))
        .catch(error => {
          console.error('Error searching TMDb:', error);
          showNotification('Error searching TMDb', 'error');
        });
    } else {
      setTmdbSearchResults([]);
    }
  };

  const handleCorrectInfo = () => {
    fetch(`http://localhost:8000/media_items/${selectedItem.id}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tmdbid: tmdbId,
          tmdbcat: tmdbCat,
        }),
      })
      .then(() => {
        fetchMediaItems();
        handleClose();
        showNotification('Media info updated successfully', 'success');
      })
      .catch(error => {
        console.error('Error updating media item:', error);
        showNotification('Error updating media item', 'error');
      });
  };

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterTitleChange = (event) => {
    setFilterTitle(event.target.value);
    setPage(0); // Reset page when filter changes
  };

  const headCells = [
    { id: 'title', numeric: false, disablePadding: false, label: 'Title' },
    { id: 'tmdbyear', numeric: true, disablePadding: false, label: 'Year' },
    { id: 'tmdbcat', numeric: false, disablePadding: false, label: 'Category' },
  ];

  return (
    <div>
      <TextField
        label="Filter by Title"
        variant="outlined"
        fullWidth
        margin="normal"
        value={filterTitle}
        onChange={handleFilterTitleChange}
      />
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="media items table">
          <TableHead>
            <TableRow>
              {headCells.map((headCell) => (
                <TableCell
                  key={headCell.id}
                  align={headCell.numeric ? 'right' : 'left'}
                  padding={headCell.disablePadding ? 'none' : 'normal'}
                  sortDirection={orderBy === headCell.id ? order : false}
                >
                  <TableSortLabel
                    active={orderBy === headCell.id}
                    direction={orderBy === headCell.id ? order : 'asc'}
                    onClick={() => handleRequestSort(headCell.id)}
                  >
                    {headCell.label}
                  </TableSortLabel>
                </TableCell>
              ))}
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mediaItems.filter(item => item.title && item.title.toLowerCase().includes(filterTitle.toLowerCase())).map((item) => (
              <TableRow
                key={item.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {item.title}
                </TableCell>
                <TableCell align="right">{item.tmdbyear}</TableCell>
                <TableCell align="right">{item.tmdbcat}</TableCell>
                <TableCell align="right">
                  <Button variant="contained" onClick={() => handleClickOpen(item)}>
                    Correct Info
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={-1} // Placeholder for total count
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Correct Media Info</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter the correct TMDb ID and category for the selected media item.
          </DialogContentText>
          <Autocomplete
            freeSolo
            options={tmdbSearchResults}
            getOptionLabel={(option) => option.title || option.name || ''}
            onInputChange={handleTmdbSearch}
            onChange={(event, newValue) => {
              if (newValue) {
                setTmdbId(newValue.id ? String(newValue.id) : '');
                setTmdbCat(newValue.media_type || '');
              }
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                margin="dense"
                label="Search TMDb"
                type="text"
                fullWidth
                variant="standard"
              />
            )}
          />
          <TextField
            margin="dense"
            id="tmdbId"
            label="TMDb ID"
            type="text"
            fullWidth
            variant="standard"
            value={tmdbId}
            onChange={(e) => setTmdbId(e.target.value)}
          />
          <TextField
            margin="dense"
            id="tmdbCat"
            label="TMDb Category"
            type="text"
            fullWidth
            variant="standard"
            value={tmdbCat}
            onChange={(e) => setTmdbCat(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleCorrectInfo}>Save</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default MediaLibraryModule;
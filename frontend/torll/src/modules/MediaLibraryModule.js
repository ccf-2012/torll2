import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TextField, 
  Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Autocomplete, 
  IconButton, Box, Collapse, Typography, useMediaQuery, useTheme, TablePagination
} from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getExpandedRowModel,
  flexRender,
} from '@tanstack/react-table';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

function MediaLibraryModule() {
  const [mediaItems, setMediaItems] = useState([]);
  const [open, setOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [tmdbId, setTmdbId] = useState('');
  const [tmdbCat, setTmdbCat] = useState('');
  const [tmdbSearchResults, setTmdbSearchResults] = useState([]);
  
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [expanded, setExpanded] = useState({});

  const { showNotification } = useNotification();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const fetchMediaItems = () => {
    const { pageIndex, pageSize } = pagination;
    const skip = pageIndex * pageSize;
    const limit = pageSize;
    const sort_by = sorting.length > 0 ? sorting[0].id : 'id';
    const sort_order = sorting.length > 0 ? (sorting[0].desc ? 'desc' : 'asc') : 'asc';

    let url = `/media_items/?skip=${skip}&limit=${limit}&sort_by=${sort_by}&sort_order=${sort_order}`;
    if (globalFilter) {
      url += `&title=${globalFilter}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setMediaItems(data))
      .catch(error => {
        console.error('Error fetching media items:', error);
        showNotification('Error fetching media items', 'error');
      });
  };

  useEffect(() => {
    fetchMediaItems();
  }, [pagination, sorting, globalFilter]);

  const handleClickOpen = (item) => {
    setSelectedItem(item);
    setTmdbId(item.tmdbid || '');
    setTmdbCat(item.tmdbcat || '');
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setTmdbSearchResults([]);
  };

  const handleTmdbSearch = (event, value) => {
    if (value && value.length > 2) {
      fetch(`/tmdb/search?query=${value}`)
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
    fetch(`/media_items/${selectedItem.id}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tmdbid: tmdbId, tmdbcat: tmdbCat }),
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

  const columns = useMemo(() => [
    {
      id: 'expander',
      header: () => null,
      cell: ({ row }) => (
        <IconButton size="small" onClick={() => row.toggleExpanded()}>
          {row.getIsExpanded() ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
      ),
    },
    { accessorKey: 'title', header: 'Title' },
    { accessorKey: 'tmdbyear', header: 'Year' },
    { accessorKey: 'tmdbcat', header: 'Category' },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <Button variant="contained" size="small" onClick={() => handleClickOpen(row.original)}>
          Correct Info
        </Button>
      ),
    },
  ], []);

  const table = useReactTable({
    data: mediaItems,
    columns,
    state: { sorting, pagination, globalFilter, expanded },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,
    onExpandedChange: setExpanded,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    manualPagination: true,
    manualSorting: true,
    manualFiltering: true,
  });

  useEffect(() => {
    table.setColumnVisibility({
      expander: isMobile,
      tmdbyear: !isMobile,
      tmdbcat: !isMobile,
    });
  }, [isMobile, table]);

  return (
    <Paper sx={{ p: { xs: 1, md: 2 }, mb: 3 }}>
      <TextField
        label="Filter by Title"
        variant="outlined"
        fullWidth
        margin="normal"
        value={globalFilter}
        onChange={e => setGlobalFilter(e.target.value)}
      />
      <TableContainer>
        <Table>
          <TableHead>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <TableCell key={header.id} colSpan={header.colSpan}>
                    {header.isPlaceholder ? null : (
                      <Box
                        sx={{ cursor: header.column.getCanSort() ? 'pointer' : 'auto' }}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {{ asc: ' 🔼', desc: ' 🔽' }[header.column.getIsSorted()] ?? null}
                      </Box>
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody>
            {table.getRowModel().rows.map(row => (
              <React.Fragment key={row.id}>
                <TableRow>
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
                {row.getIsExpanded() && (
                  <TableRow>
                    <TableCell colSpan={row.getVisibleCells().length}>
                       <Collapse in={row.getIsExpanded()} timeout="auto" unmountOnExit>
                          <Box sx={{ margin: 1 }}>
                            <Typography variant="h6" gutterBottom component="div">
                              Details
                            </Typography>
                            <Table size="small" aria-label="details">
                              <TableBody>
                                <TableRow>
                                  <TableCell>Year</TableCell>
                                  <TableCell>{row.original.tmdbyear}</TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell>Category</TableCell>
                                  <TableCell>{row.original.tmdbcat}</TableCell>
                                </TableRow>
                              </TableBody>
                            </Table>
                          </Box>
                        </Collapse>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={-1}
        rowsPerPage={table.getState().pagination.pageSize}
        page={table.getState().pagination.pageIndex}
        onPageChange={(e, newPage) => table.setPageIndex(newPage)}
        onRowsPerPageChange={e => table.setPageSize(Number(e.target.value))}
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
    </Paper>
  );
}

export default MediaLibraryModule;

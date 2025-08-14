import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TextField, 
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

function SearchModule() {
  const [searchTerm, setSearchTerm] = useState('');
  const [siteName, setSiteName] = useState('default_site'); // Placeholder
  const [searchResults, setSearchResults] = useState([]);
  
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [expanded, setExpanded] = useState({});

  const { showNotification } = useNotification();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const fetchSearchResults = () => {
    let url = '/search/cache';
    if (globalFilter) {
      url += `?title=${globalFilter}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setSearchResults(data))
      .catch(error => {
        console.error('Error fetching search results:', error);
        showNotification('Error fetching search results', 'error');
      });
  };

  useEffect(() => {
    fetchSearchResults();
  }, [globalFilter]);

  const handleSearch = () => {
    fetch('/search/pt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ search_term: searchTerm, site_name: siteName }),
    })
      .then(response => response.json())
      .then(data => {
        showNotification('Search initiated', 'info');
        setTimeout(fetchSearchResults, 2000); // Re-fetch after a delay
      })
      .catch(error => {
        console.error('Error initiating search:', error);
        showNotification('Error initiating search', 'error');
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
    { accessorKey: 'tortitle', header: 'Title' },
    { accessorKey: 'site', header: 'Site' },
    { accessorKey: 'torsizestr', header: 'Size' },
    { accessorKey: 'seednum', header: 'Seeders' },
    { accessorKey: 'downnum', header: 'Leechers' },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <Button variant="contained" size="small" onClick={() => console.log('Download:', row.original)}>
          Download
        </Button>
      ),
    },
  ], []);

  const table = useReactTable({
    data: searchResults,
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
    manualFiltering: true, // API handles filtering
  });

  useEffect(() => {
    table.setColumnVisibility({
      expander: isMobile,
      site: !isMobile,
      torsizestr: !isMobile,
      seednum: !isMobile,
      downnum: !isMobile,
    });
  }, [isMobile, table]);

  return (
    <Paper sx={{ p: { xs: 1, md: 2 }, mb: 3 }}>
      <Typography variant="h5" gutterBottom>PT Site Search</Typography>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', mb: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        <TextField label="Search Term" variant="outlined" fullWidth value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        <Button variant="contained" onClick={handleSearch} sx={{ ml: 2, whiteSpace: 'nowrap' }}>
          Search
        </Button>
      </Box>
      <TextField
        label="Filter Cached Results by Title"
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
                                <TableRow><TableCell>Site</TableCell><TableCell>{row.original.site}</TableCell></TableRow>
                                <TableRow><TableCell>Size</TableCell><TableCell>{row.original.torsizestr}</TableCell></TableRow>
                                <TableRow><TableCell>Seeders</TableCell><TableCell>{row.original.seednum}</TableCell></TableRow>
                                <TableRow><TableCell>Leechers</TableCell><TableCell>{row.original.downnum}</TableCell></TableRow>
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
        count={table.getCoreRowModel().rows.length} // Count based on fetched results
        rowsPerPage={table.getState().pagination.pageSize}
        page={table.getState().pagination.pageIndex}
        onPageChange={(e, newPage) => table.setPageIndex(newPage)}
        onRowsPerPageChange={e => table.setPageSize(Number(e.target.value))}
      />
    </Paper>
  );
}

export default SearchModule;

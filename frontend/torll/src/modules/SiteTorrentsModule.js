import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, IconButton,
  TablePagination, TextField, Box, Collapse, Typography, useMediaQuery, useTheme
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

function SiteTorrentsModule() {
  const [torrents, setTorrents] = useState([]);
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });
  const [expanded, setExpanded] = useState({});

  const { showNotification } = useNotification();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    fetchTorrents();
  }, [pagination, sorting, globalFilter]);

  const fetchTorrents = () => {
    const { pageIndex, pageSize } = pagination;
    const skip = pageIndex * pageSize;
    const limit = pageSize;
    const sort_by = sorting.length > 0 ? sorting[0].id : 'id';
    const sort_order = sorting.length > 0 ? (sorting[0].desc ? 'desc' : 'asc') : 'asc';

    let url = `/site_torrents/?skip=${skip}&limit=${limit}&sort_by=${sort_by}&sort_order=${sort_order}`;
    if (globalFilter) {
      url += `&title=${globalFilter}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setTorrents(data))
      .catch(error => {
        console.error('Error fetching site torrents:', error);
        showNotification('Error fetching site torrents', 'error');
      });
  };

  const handleDownload = (torrent) => {
    fetch('/downloads/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        download_link: torrent.downlink,
        qbit_config_name: 'default',
      }),
    })
      .then(response => response.json())
      .then(data => {
        showNotification('Torrent added to downloader', 'success');
      })
      .catch(error => {
        showNotification('Error downloading torrent', 'error');
      });
  };

  const columns = useMemo(() => [
    {
      id: 'expander',
      header: () => null,
      cell: ({ row }) => (
        <IconButton
          aria-label="expand row"
          size="small"
          onClick={() => row.toggleExpanded()}
        >
          {row.getIsExpanded() ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </IconButton>
      ),
    },
    {
      accessorKey: 'tortitle',
      header: 'Title',
      cell: info => info.getValue(),
    },
    {
      accessorKey: 'torsizestr',
      header: 'Size',
    },
    {
      accessorKey: 'seednum',
      header: 'Seeders',
    },
    {
      accessorKey: 'downnum',
      header: 'Leechers',
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <Button variant="contained" size="small" onClick={() => handleDownload(row.original)}>
          Download
        </Button>
      ),
    },
  ], []);

  const table = useReactTable({
    data: torrents,
    columns,
    state: {
      sorting,
      pagination,
      globalFilter,
      expanded,
    },
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
      torsizestr: !isMobile,
      seednum: !isMobile,
      downnum: !isMobile,
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
                                  <TableCell>Size</TableCell>
                                  <TableCell>{row.original.torsizestr}</TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell>Seeders</TableCell>
                                  <TableCell>{row.original.seednum}</TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell>Leechers</TableCell>
                                  <TableCell>{row.original.downnum}</TableCell>
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
        count={-1} // API doesn't provide total count, so we use -1
        rowsPerPage={table.getState().pagination.pageSize}
        page={table.getState().pagination.pageIndex}
        onPageChange={(e, newPage) => table.setPageIndex(newPage)}
        onRowsPerPageChange={e => table.setPageSize(Number(e.target.value))}
      />
    </Paper>
  );
}

export default SiteTorrentsModule;
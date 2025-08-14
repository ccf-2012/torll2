import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, IconButton,
  TablePagination, Box, Collapse, Typography, useMediaQuery, useTheme
} from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getExpandedRowModel,
  flexRender,
} from '@tanstack/react-table';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

function DownloadsModule() {
  const [downloads, setDownloads] = useState([]);
  const [sorting, setSorting] = useState([]);
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [expanded, setExpanded] = useState({});
  const { showNotification } = useNotification();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const fetchDownloads = () => {
    const { pageIndex, pageSize } = pagination;
    const skip = pageIndex * pageSize;
    const limit = pageSize;
    const sort_by = sorting.length > 0 ? sorting[0].id : 'id';
    const sort_order = sorting.length > 0 ? (sorting[0].desc ? 'desc' : 'asc') : 'asc';
    fetch(`/downloads/?skip=${skip}&limit=${limit}&sort_by=${sort_by}&sort_order=${sort_order}`)
      .then(response => response.json())
      .then(data => setDownloads(data))
      .catch(error => {
        console.error('Error fetching downloads:', error);
        showNotification('Error fetching downloads', 'error');
      });
  };

  useEffect(() => {
    fetchDownloads();
  }, [pagination, sorting]);

  const handleRedownload = (download) => {
    fetch(`/downloads/${download.id}/redownload`, { method: 'POST' })
      .then(() => {
        showNotification('Re-download initiated', 'info');
        fetchDownloads();
      })
      .catch(error => {
        console.error('Error re-downloading torrent:', error);
        showNotification('Error re-downloading torrent', 'error');
      });
  };

  const handleStop = (download) => {
    fetch(`/downloads/${download.id}/stop`, { method: 'POST' })
      .then(() => {
        showNotification('Torrent stopped', 'info');
        fetchDownloads();
      })
      .catch(error => {
        console.error('Error stopping torrent:', error);
        showNotification('Error stopping torrent', 'error');
      });
  };

  const handleDelete = (download) => {
    fetch(`/downloads/${download.id}`, { method: 'DELETE' })
      .then(() => {
        showNotification('Torrent deleted', 'success');
        fetchDownloads();
      })
      .catch(error => {
        console.error('Error deleting torrent:', error);
        showNotification('Error deleting torrent', 'error');
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
    { accessorKey: 'torname', header: 'Name' },
    { accessorKey: 'size', header: 'Size', cell: info => `${(info.getValue() / 1024 / 1024 / 1024).toFixed(2)} GB` },
    { accessorKey: 'site', header: 'Source' },
    { accessorKey: 'addedon', header: 'Added On', cell: info => new Date(info.getValue()).toLocaleString() },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          <Button size="small" variant="contained" onClick={() => handleRedownload(row.original)}>Re-download</Button>
          <Button size="small" variant="contained" onClick={() => handleStop(row.original)}>Stop</Button>
          <Button size="small" variant="contained" color="error" onClick={() => handleDelete(row.original)}>Delete</Button>
        </Box>
      ),
    },
  ], []);

  const table = useReactTable({
    data: downloads,
    columns,
    state: { sorting, pagination, expanded },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onExpandedChange: setExpanded,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    manualPagination: true,
    manualSorting: true,
  });

  useEffect(() => {
    table.setColumnVisibility({
      expander: isMobile,
      size: !isMobile,
      site: !isMobile,
      addedon: !isMobile,
    });
  }, [isMobile, table]);

  return (
    <Paper sx={{ p: { xs: 1, md: 2 }, mb: 3 }}>
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
                                  <TableCell>{(row.original.size / 1024 / 1024 / 1024).toFixed(2)} GB</TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell>Source</TableCell>
                                  <TableCell>{row.original.site}</TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell>Added On</TableCell>
                                  <TableCell>{new Date(row.original.addedon).toLocaleString()}</TableCell>
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
    </Paper>
  );
}

export default DownloadsModule;

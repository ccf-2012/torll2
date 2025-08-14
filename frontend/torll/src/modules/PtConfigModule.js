import React, { useState, useEffect, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TextField, 
  Dialog, DialogActions, DialogContent, DialogTitle, Checkbox, FormControlLabel, 
  IconButton, Box, Collapse, Typography, useMediaQuery, useTheme
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

function PtConfigModule() {
  const [ptSites, setPtSites] = useState([]);
  const [open, setOpen] = useState(false);
  const [currentSite, setCurrentSite] = useState(null);
  const [siteName, setSiteName] = useState('');
  const [cookie, setCookie] = useState('');
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [updateInterval, setUpdateInterval] = useState(600);
  const [siteNewLink, setSiteNewLink] = useState('');
  const [siteNewCheck, setSiteNewCheck] = useState(true);
  
  const [sorting, setSorting] = useState([]);
  const [expanded, setExpanded] = useState({});

  const { showNotification } = useNotification();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const fetchPtSites = () => {
    fetch('/pt_configs/')
      .then(response => response.json())
      .then(data => setPtSites(data))
      .catch(error => {
        console.error('Error fetching PT sites:', error);
        showNotification('Error fetching PT sites', 'error');
      });
  };

  useEffect(() => {
    fetchPtSites();
  }, []);

  const handleClickOpen = (site = null) => {
    setCurrentSite(site);
    setSiteName(site ? site.site : '');
    setCookie(site ? site.cookie : '');
    setAutoUpdate(site ? site.auto_update : true);
    setUpdateInterval(site ? site.update_interval : 600);
    setSiteNewLink(site ? site.siteNewLink : '');
    setSiteNewCheck(site ? site.siteNewCheck : true);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setCurrentSite(null);
  };

  const handleSubmit = () => {
    const siteData = {
      site: siteName,
      cookie: cookie,
      auto_update: autoUpdate,
      update_interval: updateInterval,
      siteNewLink: siteNewLink,
      siteNewCheck: siteNewCheck,
    };

    const url = currentSite ? `/pt_configs/${currentSite.id}` : '/pt_configs/';
    const method = currentSite ? 'PUT' : 'POST';

    fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(siteData),
    })
      .then(response => response.json())
      .then(() => {
        showNotification(`PT Site ${currentSite ? 'updated' : 'added'} successfully`, 'success');
        fetchPtSites();
        handleClose();
      })
      .catch(error => {
        console.error(`Error ${currentSite ? 'updating' : 'adding'} PT site:`, error);
        showNotification(`Error ${currentSite ? 'updating' : 'adding'} PT site`, 'error');
      });
  };

  const handleDelete = (id) => {
    fetch(`/pt_configs/${id}`, { method: 'DELETE' })
      .then(() => {
        showNotification('PT Site deleted successfully', 'success');
        fetchPtSites();
      })
      .catch(error => {
        console.error('Error deleting PT site:', error);
        showNotification('Error deleting PT site', 'error');
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
    { accessorKey: 'site', header: 'Site Name' },
    { accessorKey: 'auto_update', header: 'Auto Update', cell: info => info.getValue() ? 'Yes' : 'No' },
    { accessorKey: 'update_interval', header: 'Interval (s)' },
    { accessorKey: 'siteNewLink', header: 'New Link' },
    { accessorKey: 'siteNewCheck', header: 'New Check', cell: info => info.getValue() ? 'Yes' : 'No' },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Button size="small" variant="contained" onClick={() => handleClickOpen(row.original)}>Edit</Button>
          <Button size="small" variant="contained" color="error" onClick={() => handleDelete(row.original.id)}>Delete</Button>
        </Box>
      ),
    },
  ], []);

  const table = useReactTable({
    data: ptSites,
    columns,
    state: { sorting, expanded },
    onSortingChange: setSorting,
    onExpandedChange: setExpanded,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
  });

  useEffect(() => {
    table.setColumnVisibility({
      expander: isMobile,
      auto_update: !isMobile,
      update_interval: !isMobile,
      siteNewLink: !isMobile,
      siteNewCheck: !isMobile,
    });
  }, [isMobile, table]);

  return (
    <Paper sx={{ p: { xs: 1, md: 2 }, mb: 3 }}>
      <Button variant="contained" onClick={() => handleClickOpen()} sx={{ mb: 2 }}>
        Add New PT Site
      </Button>
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
                                <TableRow><TableCell>Auto Update</TableCell><TableCell>{row.original.auto_update ? 'Yes' : 'No'}</TableCell></TableRow>
                                <TableRow><TableCell>Interval</TableCell><TableCell>{row.original.update_interval}s</TableCell></TableRow>
                                <TableRow><TableCell>New Link</TableCell><TableCell>{row.original.siteNewLink}</TableCell></TableRow>
                                <TableRow><TableCell>New Check</TableCell><TableCell>{row.original.siteNewCheck ? 'Yes' : 'No'}</TableCell></TableRow>
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

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>{currentSite ? 'Edit PT Site' : 'Add New PT Site'}</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" label="Site Name" type="text" fullWidth variant="standard" value={siteName} onChange={(e) => setSiteName(e.target.value)} disabled={!!currentSite} />
          <TextField margin="dense" label="Cookie" type="text" fullWidth variant="standard" value={cookie} onChange={(e) => setCookie(e.target.value)} />
          <FormControlLabel control={<Checkbox checked={autoUpdate} onChange={(e) => setAutoUpdate(e.target.checked)}/>} label="Auto Update" />
          <TextField margin="dense" label="Update Interval (seconds)" type="number" fullWidth variant="standard" value={updateInterval} onChange={(e) => setUpdateInterval(parseInt(e.target.value))} />
          <TextField margin="dense" label="Site New Link" type="text" fullWidth variant="standard" value={siteNewLink} onChange={(e) => setSiteNewLink(e.target.value)} />
          <FormControlLabel control={<Checkbox checked={siteNewCheck} onChange={(e) => setSiteNewCheck(e.target.checked)}/>} label="Site New Check" />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit}>{currentSite ? 'Update' : 'Add'}</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

export default PtConfigModule;
import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TableSortLabel, TablePagination, TextField } from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';

function SiteTorrentsModule() {
  const [torrents, setTorrents] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('id');
  const [order, setOrder] = useState('asc'); // 'asc' or 'desc'
  const [filterTitle, setFilterTitle] = useState(''); // New state for filtering
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchTorrents();
  }, [page, rowsPerPage, orderBy, order, filterTitle]); // Add filterTitle to dependencies

  const fetchTorrents = () => {
    const skip = page * rowsPerPage;
    const limit = rowsPerPage;
    let url = `http://localhost:8000/site_torrents/?skip=${skip}&limit=${limit}&sort_by=${orderBy}&sort_order=${order}`;
    if (filterTitle) {
      url += `&title=${filterTitle}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => setTorrents(data))
      .catch(error => {
        console.error('Error fetching site torrents:', error);
        showNotification('Error fetching site torrents', 'error');
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

  const handleDownload = (torrent) => {
    fetch('http://localhost:8000/downloads/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        download_link: torrent.downlink,
        qbit_config_name: 'default', // This should be configurable
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Download response:', data);
        showNotification('Torrent added to downloader', 'success');
      })
      .catch(error => {
        console.error('Error downloading torrent:', error);
        showNotification('Error downloading torrent', 'error');
      });
  };

  const headCells = [
    { id: 'tortitle', numeric: false, disablePadding: false, label: 'Title' },
    { id: 'torsizestr', numeric: true, disablePadding: false, label: 'Size' },
    { id: 'seednum', numeric: true, disablePadding: false, label: 'Seeders' },
    { id: 'downnum', numeric: true, disablePadding: false, label: 'Leechers' },
  ];

  return (
    <Paper>
      <TextField
        label="Filter by Title"
        variant="outlined"
        fullWidth
        margin="normal"
        value={filterTitle}
        onChange={handleFilterTitleChange}
      />
      <TableContainer sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: 650, width: '100%' }} aria-label="site torrents table">
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
            {torrents.map((torrent) => (
              <TableRow
                key={torrent.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {torrent.tortitle}
                </TableCell>
                <TableCell align="right">{torrent.torsizestr}</TableCell>
                <TableCell align="right">{torrent.seednum}</TableCell>
                <TableCell align="right">{torrent.downnum}</TableCell>
                <TableCell align="right">
                  <Button variant="contained" onClick={() => handleDownload(torrent)}>
                    Download
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
        count={-1} // Placeholder for total count, will need another API call for actual count
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}

export default SiteTorrentsModule;

import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TableSortLabel, TablePagination } from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';

function DownloadsModule() {
  const [downloads, setDownloads] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('id');
  const [order, setOrder] = useState('asc'); // 'asc' or 'desc'
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchDownloads();
  }, [page, rowsPerPage, orderBy, order]);

  const fetchDownloads = () => {
    const skip = page * rowsPerPage;
    const limit = rowsPerPage;
    fetch(`http://localhost:8000/downloads/?skip=${skip}&limit=${limit}&sort_by=${orderBy}&sort_order=${order}`)
      .then(response => response.json())
      .then(data => setDownloads(data))
      .catch(error => {
        console.error('Error fetching downloads:', error);
        showNotification('Error fetching downloads', 'error');
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

  const handleRedownload = (download) => {
    fetch(`http://localhost:8000/downloads/${download.id}/redownload`, { method: 'POST' })
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
    fetch(`http://localhost:8000/downloads/${download.id}/stop`, { method: 'POST' })
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
    fetch(`http://localhost:8000/downloads/${download.id}`, { method: 'DELETE' })
      .then(() => {
        showNotification('Torrent deleted', 'success');
        fetchDownloads();
      })
      .catch(error => {
        console.error('Error deleting torrent:', error);
        showNotification('Error deleting torrent', 'error');
      });
  };

  const headCells = [
    { id: 'torname', numeric: false, disablePadding: false, label: 'Name' },
    { id: 'size', numeric: true, disablePadding: false, label: 'Size' },
    { id: 'site', numeric: false, disablePadding: false, label: 'Source' },
    { id: 'addedon', numeric: false, disablePadding: false, label: 'Added On' },
  ];

  return (
    <Paper>
      <TableContainer sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: 650, width: '100%' }} aria-label="downloads table">
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
            {downloads.map((download) => (
              <TableRow
                key={download.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {download.torname}
                </TableCell>
                <TableCell align="right">{download.size}</TableCell>
                <TableCell align="right">{download.site}</TableCell>
                <TableCell align="right">{new Date(download.addedon).toLocaleString()}</TableCell>
                <TableCell align="right">
                  <Button onClick={() => handleRedownload(download)}>Re-download</Button>
                  <Button onClick={() => handleStop(download)}>Stop</Button>
                  <Button onClick={() => handleDelete(download)}>Delete</Button>
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
    </Paper>
  );
}

export default DownloadsModule;
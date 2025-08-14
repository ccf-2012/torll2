import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, TextField, Dialog, DialogActions, DialogContent, DialogTitle, Checkbox, FormControlLabel } from '@mui/material';
import { useNotification } from '../contexts/NotificationContext';

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
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchPtSites();
  }, []);

  const fetchPtSites = () => {
    fetch('http://localhost:8000/pt_configs/')
      .then(response => response.json())
      .then(data => setPtSites(data))
      .catch(error => {
        console.error('Error fetching PT sites:', error);
        showNotification('Error fetching PT sites', 'error');
      });
  };

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

    if (currentSite) {
      // Update existing site
      fetch(`http://localhost:8000/pt_configs/${currentSite.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(siteData),
      })
        .then(response => response.json())
        .then(() => {
          showNotification('PT Site updated successfully', 'success');
          fetchPtSites();
          handleClose();
        })
        .catch(error => {
          console.error('Error updating PT site:', error);
          showNotification('Error updating PT site', 'error');
        });
    } else {
      // Add new site
      fetch('http://localhost:8000/pt_configs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(siteData),
      })
        .then(response => response.json())
        .then(() => {
          showNotification('PT Site added successfully', 'success');
          fetchPtSites();
          handleClose();
        })
        .catch(error => {
          console.error('Error adding PT site:', error);
          showNotification('Error adding PT site', 'error');
        });
    }
  };

  const handleDelete = (id) => {
    fetch(`http://localhost:8000/pt_configs/${id}`, {
      method: 'DELETE',
    })
      .then(() => {
        showNotification('PT Site deleted successfully', 'success');
        fetchPtSites();
      })
      .catch(error => {
        console.error('Error deleting PT site:', error);
        showNotification('Error deleting PT site', 'error');
      });
  };

  return (
    <Paper>
      <Button variant="contained" onClick={() => handleClickOpen()}>
        Add New PT Site
      </Button>
      <TableContainer sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: 650, width: '100%' }} aria-label="PT sites table">
          <TableHead>
            <TableRow>
              <TableCell>Site Name</TableCell>
              <TableCell>Auto Update</TableCell>
              <TableCell>Update Interval</TableCell>
              <TableCell>Site New Link</TableCell>
              <TableCell>Site New Check</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ptSites.map((site) => (
              <TableRow key={site.id}>
                <TableCell>{site.site}</TableCell>
                <TableCell>{site.auto_update ? 'Yes' : 'No'}</TableCell>
                <TableCell>{site.update_interval}</TableCell>
                <TableCell>{site.siteNewLink}</TableCell>
                <TableCell>{site.siteNewCheck ? 'Yes' : 'No'}</TableCell>
                <TableCell>
                  <Button onClick={() => handleClickOpen(site)}>Edit</Button>
                  <Button onClick={() => handleDelete(site.id)}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>{currentSite ? 'Edit PT Site' : 'Add New PT Site'}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Site Name"
            type="text"
            fullWidth
            variant="standard"
            value={siteName}
            onChange={(e) => setSiteName(e.target.value)}
            disabled={!!currentSite} // Disable site name editing for existing sites
          />
          <TextField
            margin="dense"
            label="Cookie"
            type="text"
            fullWidth
            variant="standard"
            value={cookie}
            onChange={(e) => setCookie(e.target.value)}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={autoUpdate}
                onChange={(e) => setAutoUpdate(e.target.checked)}
              />
            }
            label="Auto Update"
          />
          <TextField
            margin="dense"
            label="Update Interval (seconds)"
            type="number"
            fullWidth
            variant="standard"
            value={updateInterval}
            onChange={(e) => setUpdateInterval(parseInt(e.target.value))}
          />
          <TextField
            margin="dense"
            label="Site New Link"
            type="text"
            fullWidth
            variant="standard"
            value={siteNewLink}
            onChange={(e) => setSiteNewLink(e.target.value)}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={siteNewCheck}
                onChange={(e) => setSiteNewCheck(e.target.checked)}
              />
            }
            label="Site New Check"
          />
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

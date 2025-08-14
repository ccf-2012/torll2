import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Box, useMediaQuery, useTheme, Button } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { RssFeed, Storage, GetApp, VideoLibrary, Search, Settings } from '@mui/icons-material'; // Import Settings icon
import { Link } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: 'RSS', icon: <RssFeed />, path: '/' },
  { text: 'Site Torrents', icon: <Storage />, path: '/site-torrents' },
  { text: 'Downloads', icon: <GetApp />, path: '/downloads' },
  { text: 'Media Library', icon: <VideoLibrary />, path: '/media-library' },
  { text: 'Search', icon: <Search />, path: '/search' },
  { text: 'PT Configs', icon: <Settings />, path: '/pt-configs' }, // New menu item
];

function Layout({ children }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <div>
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text} component={Link} to={item.path} onClick={isMobile ? handleDrawerToggle : null}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Torll
          </Typography>
          {!isMobile && (
            <Box sx={{ display: { xs: 'none', md: 'block' } }}>
              {menuItems.map((item) => (
                <Button key={item.text} color="inherit" component={Link} to={item.path}>
                  {item.text}
                </Button>
              ))}
            </Box>
          )}
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="mailbox folders"
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile.
            }}
            sx={{
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
        ) : (
          null
        )}
      </Box>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 0, m: 0, width: '100%' }} // Explicitly set padding, margin, and width
      >
        <Toolbar /> {/* This is to offset content below the AppBar */}
        {children}
      </Box>
    </Box>
  );
}

export default Layout;
import { createTheme } from '@mui/material/styles';

// A custom theme for this app
const theme = createTheme({
  palette: {
    primary: {
      main: '#556cd6', // A nice indigo
    },
    secondary: {
      main: '#19857b', // A complementary teal
    },
    error: {
      main: '#ff1744',
    },
    background: {
      default: '#f4f6f8',
    },
  },
});

export default theme;

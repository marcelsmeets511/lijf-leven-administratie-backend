// frontend/src/App.js

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import {
  AppBar,
  Box,
  Button,
  Container,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  ThemeProvider,
  createTheme,
  Divider // Toegevoegd voor visuele scheiding
} from '@mui/material';

// Importeer Icons
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import PeopleIcon from '@mui/icons-material/People'; // Clients
import MedicalServicesIcon from '@mui/icons-material/MedicalServices'; // Treatment Methods
import PostAddIcon from '@mui/icons-material/PostAdd'; // Treatments (Registratie)
import DescriptionIcon from '@mui/icons-material/Description'; // Invoices
import CloseIcon from '@mui/icons-material/Close'; // Voor sluiten drawer

// Importeer je pagina componenten
import ClientsPage from './pages/ClientsPage';
import TreatmentMethodsPage from './pages/TreatmentMethodsPage';
import TreatmentsPage from './pages/TreatmentsPage';
import InvoicesPage from './pages/InvoicesPage';

// Definieer de breedte van de mobiele drawer
const drawerWidth = 250;

// Definieer de navigatie-items
const navItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/' },
  { text: 'Cliënten', icon: <PeopleIcon />, path: '/clients' },
  { text: 'Methodes', icon: <MedicalServicesIcon />, path: '/methods' },
  { text: 'Behandelingen', icon: <PostAddIcon />, path: '/treatments' },
  { text: 'Facturen', icon: <DescriptionIcon />, path: '/invoices' },
];

// Maak een basis MUI thema
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Standaard MUI blauw
    },
    // Je kunt hier meer aanpassingen doen
  },
  // Voeg hier eventueel custom breakpoints of andere thema overrides toe
});

// Simpele Home Page component
const HomePage = () => (
    <Box>
        <Typography variant="h4" gutterBottom>Welkom bij de Facturatie Applicatie</Typography>
        <Typography variant="body1">
            Selecteer een optie uit het menu hierboven (desktop) of via het menu-icoon (mobiel) om te beginnen.
        </Typography>
        {/* Hier kun je een dashboard-achtig overzicht toevoegen */}
    </Box>
);

// Simpele 404 pagina
const NotFoundPage = () => (
    <Box sx={{ textAlign: 'center', mt: 5 }}>
        <Typography variant="h3" gutterBottom>404 - Pagina Niet Gevonden</Typography>
        <Typography variant="body1">
            Sorry, de pagina die je zoekt bestaat niet.
        </Typography>
        <Button component={NavLink} to="/" variant="contained" sx={{ mt: 3 }}>
            Terug naar Home
        </Button>
    </Box>
);


function App() {
  const [mobileOpen, setMobileOpen] = useState(false); // State voor mobiele drawer

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Inhoud van de mobiele Drawer
  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', p:1}}>
        <Typography variant="h6" sx={{ my: 2, ml: 1 }}>
            Menu
        </Typography>
        <IconButton>
            <CloseIcon />
        </IconButton>
      </Box>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            {/* Gebruik NavLink voor actieve state */}
            <ListItemButton component={NavLink} to={item.path} sx={{ textAlign: 'left' }}
               style={({ isActive }) => ({ // Styling voor actieve link
                 backgroundColor: isActive ? theme.palette.action.hover : 'transparent',
               })}
            >
              <ListItemIcon sx={{minWidth: '40px'}}> {/* Zorg voor consistente ruimte */}
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}> {/* Hoofd container */}
          <CssBaseline />

          {/* AppBar bovenaan */}
          <AppBar component="nav" position="sticky"> {/* Sticky blijft bovenaan bij scrollen */}
            <Toolbar>
              {/* Menu knop (alleen mobiel) */}
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }} // Alleen tonen op mobiel
              >
                <MenuIcon />
              </IconButton>

              {/* App Titel */}
              <Typography
                variant="h6"
                component={NavLink} // Maak titel klikbaar naar home
                to="/"
                sx={{ flexGrow: 1, color: 'inherit', textDecoration: 'none' }}
              >
                Facturatie App
              </Typography>

              {/* Navigatie Knoppen (alleen desktop) */}
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                {navItems.map((item) => (
                   // Gebruik NavLink voor actieve state (subtiele styling)
                  <Button
                    key={item.text}
                    component={NavLink}
                    to={item.path}
                    sx={{ color: '#fff' }} // Witte tekst
                    style={({ isActive }) => ({ // Styling voor actieve link
                        fontWeight: isActive ? 'bold' : 'normal',
                        textDecoration: isActive ? 'underline' : 'none', // Onderstreping voor actief
                        textUnderlineOffset: '4px', // Beetje ruimte voor onderstreping
                    })}
                  >
                    {item.text}
                  </Button>
                ))}
              </Box>
            </Toolbar>
          </AppBar>

          {/* Mobiele Drawer */}
          <Box component="nav">
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle} // Sluit ook bij klikken buiten de drawer
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
              sx={{
                display: { xs: 'block', sm: 'none' }, // Alleen mobiel
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
          </Box>

          {/* Hoofd Content Area */}
          <Container component="main" sx={{ mt: 4, mb: 4, flexGrow: 1 }}> {/* Container voor centreren en padding */}
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/clients" element={<ClientsPage />} />
              <Route path="/methods" element={<TreatmentMethodsPage />} />
              <Route path="/treatments" element={<TreatmentsPage />} />
              <Route path="/invoices" element={<InvoicesPage />} />
              <Route path="*" element={<NotFoundPage />} /> {/* Catch-all voor 404 */}
            </Routes>
          </Container>

           {/* Optioneel: Footer */}
           <Box component="footer" sx={{ bgcolor: 'background.paper', p: 2, mt: 'auto' }}>
               <Typography variant="body2" color="text.secondary" align="center">
                 © {new Date().getFullYear()} Facturatie App
               </Typography>
           </Box>

        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;

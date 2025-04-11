// frontend/src/App.js

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Button, // <<< HIER TOEGEVOEGD
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
  ThemeProvider, // Voor theming
  createTheme, // Om een thema te maken
  useMediaQuery // Om te checken of we op mobiel zijn
} from '@mui/material';

// Importeer Icons
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import PeopleIcon from '@mui/icons-material/People'; // Clients
import MedicalServicesIcon from '@mui/icons-material/MedicalServices'; // Treatment Methods
import PostAddIcon from '@mui/icons-material/PostAdd'; // Treatments (Registratie)
import DescriptionIcon from '@mui/icons-material/Description'; // Invoices

// Importeer je pagina componenten
import ClientsPage from './pages/ClientsPage';
import TreatmentMethodsPage from './pages/TreatmentMethodsPage';
import TreatmentsPage from './pages/TreatmentsPage';
import InvoicesPage from './pages/InvoicesPage';

// Definieer de breedte van de drawer
const drawerWidth = 240;

// Definieer de navigatie-items
const navItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/' },
  { text: 'Cliënten', icon: <PeopleIcon />, path: '/clients' },
  { text: 'Methodes', icon: <MedicalServicesIcon />, path: '/methods' },
  { text: 'Behandelingen', icon: <PostAddIcon />, path: '/treatments' },
  { text: 'Facturen', icon: <DescriptionIcon />, path: '/invoices' },
];

// Maak een basis MUI thema (kan later uitgebreid worden)
const theme = createTheme({
  palette: {
    // Je kunt hier kleuren aanpassen
    // primary: { main: '#1976d2' },
    // secondary: { main: '#dc004e' },
  },
  // Je kunt hier typografie aanpassen
});

// Simpele Home Page component (als je die nog niet had)
const HomePage = () => (
    <Box>
        <Typography variant="h4" gutterBottom>Welkom bij de Facturatie Applicatie</Typography>
        <Typography variant="body1">
            Gebruik het menu aan de linkerkant (of via het icoon op mobiel) om te navigeren tussen de verschillende onderdelen.
        </Typography>
    </Box>
);


function App() {
  const [mobileOpen, setMobileOpen] = useState(false); // State voor mobiele drawer
  const location = useLocation(); // Huidige route informatie

  // Huidige pagina naam vinden voor de AppBar titel
  const currentPage = navItems.find(item => item.path === location.pathname);
  const currentPageTitle = currentPage ? currentPage.text : "Facturatie App";

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Inhoud van de Drawer (navigatie)
  const drawerContent = (
    <div>
      <Toolbar>
        {/* Optioneel: Logo of App naam in de Drawer */}
        <Typography variant="h6" noWrap component="div">
           Menu
        </Typography>
      </Toolbar>
      {/* <Divider /> */}
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={NavLink} // Gebruik NavLink voor active state
              to={item.path}
              onClick={handleDrawerToggle} // Sluit mobiele drawer na klik
              // Styling voor actieve link
              style={({ isActive }) => ({
                 backgroundColor: isActive ? theme.palette.action.selected : 'transparent',
                 // color: isActive ? theme.palette.primary.main : 'inherit', // Optioneel: kleur aanpassen
              })}
            >
              <ListItemIcon>
                {/* Actieve state kleur voor icoon (optioneel) */}
                {/* React.cloneElement(item.icon, { color: location.pathname === item.path ? 'primary' : 'inherit' }) */}
                 {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <ThemeProvider theme={theme}> {/* Wrap met ThemeProvider */}
      <Router> {/* Router blijft buiten de layout componenten */}
          <Box sx={{ display: 'flex' }}> {/* Hoofd layout container */}
            <CssBaseline /> {/* Basis CSS reset */}

            {/* AppBar bovenaan */}
            <AppBar
              position="fixed" // Houdt AppBar vast bovenaan
              sx={{
                // Zorg dat AppBar boven de permanente drawer uitsteekt op desktop
                width: { sm: `calc(100% - ${drawerWidth}px)` },
                ml: { sm: `${drawerWidth}px` },
              }}
            >
              <Toolbar>
                {/* Menu knop voor mobiel */}
                <IconButton
                  color="inherit"
                  aria-label="open drawer"
                  edge="start"
                  onClick={handleDrawerToggle}
                  sx={{ mr: 2, display: { sm: 'none' } }} // Alleen tonen op mobiel (smaller than sm)
                >
                  <MenuIcon />
                </IconButton>
                {/* Pagina Titel */}
                <Typography variant="h6" noWrap component="div">
                  {currentPageTitle}
                </Typography>
              </Toolbar>
            </AppBar>

            {/* Navigatie Drawer */}
            <Box
              component="nav"
              sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
              aria-label="mailbox folders"
            >
              {/* Tijdelijke Drawer voor mobiel */}
              <Drawer
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{
                  keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                  display: { xs: 'block', sm: 'none' }, // Alleen tonen op mobiel
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
              >
                {drawerContent}
              </Drawer>

              {/* Permanente Drawer voor desktop */}
              <Drawer
                variant="permanent"
                sx={{
                  display: { xs: 'none', sm: 'block' }, // Alleen tonen op desktop
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
                open // Permanent is altijd open
              >
                {drawerContent}
              </Drawer>
            </Box>

            {/* Hoofd Content Area */}
            <Box
              component="main"
              sx={{
                 flexGrow: 1, // Neemt resterende ruimte
                 p: 3, // Padding rondom content
                 width: { sm: `calc(100% - ${drawerWidth}px)` } // Breedte op desktop
               }}
            >
              {/* Toolbar dient als 'spacer' om content onder de vaste AppBar te duwen */}
              <Toolbar />

              {/* Hier worden de paginas gerenderd door de Router */}
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/clients" element={<ClientsPage />} />
                <Route path="/methods" element={<TreatmentMethodsPage />} />
                <Route path="/treatments" element={<TreatmentsPage />} />
                <Route path="/invoices" element={<InvoicesPage />} />
                {/* Voeg hier eventueel een 404 Not Found route toe */}
                 <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Box>
          </Box>
      </Router>
    </ThemeProvider>
  );
}

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


// Function component wrapper nodig om useLocation te gebruiken buiten de Router context in App
// Dit is niet strikt nodig als we de router *binnen* App laten, zoals hierboven.
// Als je App buiten de Router zou plaatsen, heb je een wrapper nodig:
/*
const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);
export default AppWrapper;
*/

// Omdat Router nu binnen App zit, kunnen we App direct exporteren
export default App;


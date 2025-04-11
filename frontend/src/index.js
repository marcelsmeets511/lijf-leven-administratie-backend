import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link as RouterLink } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import ClientsPage from './pages/ClientsPage';
import TreatmentMethodsPage from './pages/TreatmentMethodsPage';
import TreatmentsPage from './pages/TreatmentsPage';
import InvoicesPage from './pages/InvoicesPage';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Facturatie App
            </Typography>
            <Button color="inherit" component={RouterLink} to="/">Home</Button>
            <Button color="inherit" component={RouterLink} to="/clients">Cliënten</Button>
            <Button color="inherit" component={RouterLink} to="/methods">Methodes</Button>
            <Button color="inherit" component={RouterLink} to="/treatments">Behandelingen</Button>
            <Button color="inherit" component={RouterLink} to="/invoices">Facturen</Button>
          </Toolbar>
        </AppBar>
      </Box>
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/methods" element={<TreatmentMethodsPage />} />
          <Route path="/treatments" element={<TreatmentsPage />} />
          <Route path="/invoices" element={<InvoicesPage />} />
        </Routes>
      </Container>
    </Router>
  );
}

// Simpele Home Page component
const HomePage = () => (
  <Typography variant="h4">Welkom bij de Facturatie Applicatie</Typography>
);

export default App;

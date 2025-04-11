// frontend/src/pages/ClientsPage.js

import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Paper,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import { getClients, addClient } from '../services/api'; // Importeer API functies

function ClientsPage() {
  // State voor de lijst van cliënten
  const [clients, setClients] = useState([]);
  // State voor het formulier
  const [newClientName, setNewClientName] = useState('');
  const [newClientEmail, setNewClientEmail] = useState('');
  const [newClientPhone, setNewClientPhone] = useState('');
  // State voor laden en fouten/success berichten
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false); // Aparte state voor submit laden
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Functie om cliënten op te halen
  const fetchClients = async () => {
    setIsLoading(true);
    setError(''); // Reset error bij nieuwe fetch
    try {
      const response = await getClients();
      setClients(response.data);
    } catch (err) {
      console.error("Error fetching clients:", err);
      setError('Kon cliënten niet laden. Controleer de API verbinding.');
    } finally {
      setIsLoading(false);
    }
  };

  // Haal cliënten op bij het laden van de component
  useEffect(() => {
    fetchClients();
  }, []); // Lege dependency array zorgt dat dit alleen bij mount runt

  // Functie om het formulier te submitten
  const handleSubmit = async (event) => {
    event.preventDefault(); // Voorkom standaard browser submit
    setError('');
    setSuccess('');

    if (!newClientName.trim()) {
      setError('Naam is een verplicht veld.');
      return;
    }

    setIsSubmitting(true);
    const clientData = {
      name: newClientName,
      email: newClientEmail,
      phone: newClientPhone,
      // Voeg hier eventueel andere velden toe (address, zip_code, city)
      // als je die in je formulier en API hebt opgenomen.
    };

    try {
      await addClient(clientData);
      setSuccess(`Cliënt '${newClientName}' succesvol toegevoegd!`);
      // Reset formulier velden
      setNewClientName('');
      setNewClientEmail('');
      setNewClientPhone('');
      // Haal de lijst opnieuw op om de nieuwe cliënt te tonen
      fetchClients();
    } catch (err) {
      console.error("Error adding client:", err);
      // Probeer een specifiekere error van de backend te pakken, anders een generieke
      setError(err.response?.data?.error || 'Kon cliënt niet toevoegen.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box sx={{ maxWidth: '800px', margin: 'auto' }}> {/* Max breedte voor leesbaarheid */}
      <Typography variant="h4" gutterBottom component="h1">
        Cliënten Beheer
      </Typography>

      {/* Sectie voor toevoegen nieuwe cliënt */}
      <Paper sx={{ p: 2, mb: 4 }} elevation={3}>
        <Typography variant="h6" gutterBottom>
          Nieuwe Cliënt Toevoegen
        </Typography>
        {/* Toon foutmeldingen specifiek voor het formulier */}
        {error && !isLoading && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="name"
            label="Naam Cliënt"
            name="name"
            autoComplete="name"
            autoFocus
            value={newClientName}
            onChange={(e) => setNewClientName(e.target.value)}
            disabled={isSubmitting}
          />
          <TextField
            margin="normal"
            fullWidth
            id="email"
            label="E-mailadres"
            name="email"
            autoComplete="email"
            value={newClientEmail}
            onChange={(e) => setNewClientEmail(e.target.value)}
            disabled={isSubmitting}
          />
          <TextField
            margin="normal"
            fullWidth
            id="phone"
            label="Telefoonnummer"
            name="phone"
            autoComplete="tel"
            value={newClientPhone}
            onChange={(e) => setNewClientPhone(e.target.value)}
            disabled={isSubmitting}
          />
          {/* Voeg hier eventueel meer velden toe */}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Cliënt Opslaan'}
          </Button>
        </Box>
      </Paper>

      {/* Sectie voor lijst van bestaande cliënten */}
      <Typography variant="h5" gutterBottom>
        Bestaande Cliënten
      </Typography>

      {/* Toon algemene foutmelding bij laden */}
      {error && isLoading && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      ) : clients.length === 0 ? (
        <Typography sx={{ mt: 2 }}>Geen cliënten gevonden.</Typography>
      ) : (
        <Paper elevation={1} sx={{ mt: 2 }}>
           {/* Gebruik List voor semantiek en styling */}
          <List>
            {clients.map((client, index) => (
              <React.Fragment key={client.id}>
                <ListItem>
                  <ListItemText
                    primary={client.name}
                    secondary={
                      <>
                        {client.email && `Email: ${client.email}`}
                        {client.email && client.phone && ' | '}
                        {client.phone && `Tel: ${client.phone}`}
                      </>
                    }
                  />
                  {/* Hier kun je later knoppen toevoegen voor Bewerken/Verwijderen */}
                  {/* <Button size="small">Bewerk</Button> */}
                </ListItem>
                {/* Voeg een divider toe tussen items, behalve na de laatste */}
                {index < clients.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}

export default ClientsPage;

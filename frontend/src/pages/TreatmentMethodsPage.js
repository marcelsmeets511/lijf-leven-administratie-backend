// frontend/src/pages/TreatmentMethodsPage.js

import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  InputAdornment // Voor het euroteken
} from '@mui/material';
import { getTreatmentMethods, addTreatmentMethod } from '../services/api';

function TreatmentMethodsPage() {
  const [methods, setMethods] = useState([]);
  // Form state
  const [newMethodName, setNewMethodName] = useState('');
  const [newBillingType, setNewBillingType] = useState(''); // 'hourly' or 'session'
  const [newRate, setNewRate] = useState('');
  // Loading/Messaging state
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Functie om methodes op te halen
  const fetchMethods = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await getTreatmentMethods();
      setMethods(response.data);
    } catch (err) {
      console.error("Error fetching treatment methods:", err);
      setError('Kon behandelmethodes niet laden.');
    } finally {
      setIsLoading(false);
    }
  };

  // Haal data op bij mount
  useEffect(() => {
    fetchMethods();
  }, []);

  // Functie voor formulier submit
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!newMethodName.trim() || !newBillingType || !newRate) {
      setError('Vul alle verplichte velden in.');
      return;
    }
    if (isNaN(parseFloat(newRate)) || parseFloat(newRate) < 0) {
        setError('Voer een geldig, positief tarief in.');
        return;
    }

    setIsSubmitting(true);
    const methodData = {
      name: newMethodName,
      billing_type: newBillingType,
      rate: parseFloat(newRate), // Zorg dat het een nummer is
    };

    try {
      await addTreatmentMethod(methodData);
      setSuccess(`Methode '${newMethodName}' succesvol toegevoegd!`);
      // Reset form
      setNewMethodName('');
      setNewBillingType('');
      setNewRate('');
      // Refresh list
      fetchMethods();
    } catch (err) {
      console.error("Error adding treatment method:", err);
      setError(err.response?.data?.error || 'Kon methode niet toevoegen.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Helper om billing type leesbaar te maken
  const formatBillingType = (type) => {
    if (type === 'hourly') return 'Per Uur';
    if (type === 'session') return 'Per Sessie';
    return type;
  };

  // Helper om tarief te formatteren
  const formatRate = (rate) => {
    return new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR' }).format(rate);
  };

  return (
    <Box sx={{ maxWidth: '900px', margin: 'auto' }}>
      <Typography variant="h4" gutterBottom component="h1">
        Behandelmethodes Beheer
      </Typography>

      {/* Formulier sectie */}
      <Paper sx={{ p: 2, mb: 4 }} elevation={3}>
        <Typography variant="h6" gutterBottom>
          Nieuwe Methode Toevoegen
        </Typography>
        {error && !isLoading && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="name"
            label="Naam Methode"
            name="name"
            value={newMethodName}
            onChange={(e) => setNewMethodName(e.target.value)}
            disabled={isSubmitting}
          />
          <FormControl fullWidth margin="normal" required disabled={isSubmitting}>
            <InputLabel id="billing-type-label">Type Facturering</InputLabel>
            <Select
              labelId="billing-type-label"
              id="billing-type"
              value={newBillingType}
              label="Type Facturering"
              onChange={(e) => setNewBillingType(e.target.value)}
            >
              <MenuItem value={'hourly'}>Per Uur</MenuItem>
              <MenuItem value={'session'}>Per Sessie</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="normal"
            required
            fullWidth
            id="rate"
            label="Tarief"
            name="rate"
            type="number"
            inputProps={{ step: "0.01", min: "0" }} // Steps en minimum waarde
             InputProps={{
                startAdornment: <InputAdornment position="start">€</InputAdornment>,
             }}
            value={newRate}
            onChange={(e) => setNewRate(e.target.value)}
            disabled={isSubmitting}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Methode Opslaan'}
          </Button>
        </Box>
      </Paper>

      {/* Lijst/Tabel sectie */}
      <Typography variant="h5" gutterBottom>
        Bestaande Behandelmethodes
      </Typography>
      {error && isLoading && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      ) : methods.length === 0 ? (
        <Typography sx={{ mt: 2 }}>Geen behandelmethodes gevonden.</Typography>
      ) : (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table sx={{ minWidth: 650 }} aria-label="treatment methods table">
            <TableHead>
              <TableRow>
                <TableCell>Naam Methode</TableCell>
                <TableCell>Type Facturering</TableCell>
                <TableCell align="right">Tarief</TableCell>
                {/* <TableCell>Acties</TableCell> */}
              </TableRow>
            </TableHead>
            <TableBody>
              {methods.map((method) => (
                <TableRow key={method.id}>
                  <TableCell component="th" scope="row">
                    {method.name}
                  </TableCell>
                  <TableCell>{formatBillingType(method.billing_type)}</TableCell>
                  <TableCell align="right">{formatRate(method.rate)}</TableCell>
                  {/* <TableCell> Placeholder voor Edit/Delete </TableCell> */}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

export default TreatmentMethodsPage;

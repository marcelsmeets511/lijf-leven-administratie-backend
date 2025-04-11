import React, { useState, useEffect } from 'react';
import {
  Typography, Box, TextField, Button, Select, MenuItem, FormControl, InputLabel,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Alert
} from '@mui/material';
import { getTreatments, addTreatment, getClients, getTreatmentMethods } from '../services/api';

function TreatmentsPage() {
  const [treatments, setTreatments] = useState([]);
  const [clients, setClients] = useState([]);
  const [methods, setMethods] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [selectedClient, setSelectedClient] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [treatmentDate, setTreatmentDate] = useState(''); // Gebruik een DatePicker in een echte app
  const [duration, setDuration] = useState('');
  const [notes, setNotes] = useState('');

  const fetchAllData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [treatmentsRes, clientsRes, methodsRes] = await Promise.all([
        getTreatments(),
        getClients(),
        getTreatmentMethods()
      ]);
      setTreatments(treatmentsRes.data);
      setClients(clientsRes.data);
      setMethods(methodsRes.data);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError('Kon data niet laden. Probeer opnieuw.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    // Zoek geselecteerde methode om type te bepalen (vereenvoudigd)
    const method = methods.find(m => m.id === selectedMethod);
    const isHourly = method?.billing_type === 'hourly';

    if (!selectedClient || !selectedMethod || !treatmentDate || (isHourly && !duration)) {
        setError('Vul alle vereiste velden in (incl. duur indien per uur).');
        setIsLoading(false);
        return;
    }


    const treatmentData = {
      client_id: selectedClient,
      treatment_method_id: selectedMethod,
      treatment_date: treatmentDate, // Zorg dat dit YYYY-MM-DD formaat is
      duration_hours: isHourly ? parseFloat(duration) : null,
      notes: notes
    };

    try {
      await addTreatment(treatmentData);
      setSuccess('Behandeling succesvol toegevoegd!');
      // Reset form
      setSelectedClient('');
      setSelectedMethod('');
      setTreatmentDate('');
      setDuration('');
      setNotes('');
      // Refresh list
      fetchAllData();
    } catch (err) {
      console.error("Error adding treatment:", err);
      setError(err.response?.data?.error || 'Kon behandeling niet toevoegen.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Behandelingen Registreren</Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6">Nieuwe Behandeling</Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <FormControl fullWidth margin="normal" required>
            <InputLabel id="client-select-label">Cliënt</InputLabel>
            <Select
              labelId="client-select-label"
              id="client-select"
              value={selectedClient}
              label="Cliënt"
              onChange={(e) => setSelectedClient(e.target.value)}
            >
              {clients.map((client) => (
                <MenuItem key={client.id} value={client.id}>{client.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal" required>
            <InputLabel id="method-select-label">Behandelmethode</InputLabel>
            <Select
              labelId="method-select-label"
              id="method-select"
              value={selectedMethod}
              label="Behandelmethode"
              onChange={(e) => setSelectedMethod(e.target.value)}
            >
              {methods.map((method) => (
                <MenuItem key={method.id} value={method.id}>
                  {method.name} ({method.billing_type === 'hourly' ? 'per uur' : 'per sessie'})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            margin="normal"
            required
            fullWidth
            id="treatmentDate"
            label="Datum (YYYY-MM-DD)"
            name="treatmentDate"
            type="date" // Gebruik een MUI DatePicker voor betere UX
            InputLabelProps={{ shrink: true }}
            value={treatmentDate}
            onChange={(e) => setTreatmentDate(e.target.value)}
          />

          {/* Toon duur alleen als type 'hourly' is */}
           {methods.find(m => m.id === selectedMethod)?.billing_type === 'hourly' && (
             <TextField
                margin="normal"
                required
                fullWidth
                id="duration"
                label="Duur (uren, bv. 1.5)"
                name="duration"
                type="number"
                inputProps={{ step: "0.1" }}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
           )}


          <TextField
            margin="normal"
            fullWidth
            id="notes"
            label="Notities"
            name="notes"
            multiline
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <Button
            type="submit"
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? 'Bezig...' : 'Behandeling Opslaan'}
          </Button>
        </Box>
      </Paper>

      <Typography variant="h5" gutterBottom>Geregistreerde Behandelingen</Typography>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Datum</TableCell>
              <TableCell>Cliënt</TableCell>
              <TableCell>Methode</TableCell>
              <TableCell>Duur/Sessie</TableCell>
              <TableCell>Notities</TableCell>
              <TableCell>Gefactureerd?</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={6}>Laden...</TableCell></TableRow>}
            {!isLoading && treatments.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{new Date(row.treatment_date).toLocaleDateString('nl-NL')}</TableCell>
                <TableCell>{row.client_name}</TableCell>
                <TableCell>{row.method_name}</TableCell>
                <TableCell>{row.billing_type === 'hourly' ? `${row.duration_hours} uur` : 'Sessie'}</TableCell>
                <TableCell>{row.notes}</TableCell>
                <TableCell>{row.is_billed ? 'Ja' : 'Nee'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default TreatmentsPage;

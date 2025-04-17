// frontend/src/pages/InvoicesPage.js

import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  IconButton, // Voor icoon knoppen
  Link // Om download links te maken
} from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'; // PDF icoon
import DescriptionIcon from '@mui/icons-material/Description'; // Generic doc/XLS icoon
import { getInvoices, generateInvoices, getInvoicePdfUrl, getInvoiceXlsUrl } from '../services/api';

function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(''); // Voor generatie success

  // Functie om facturen op te halen
  const fetchInvoices = async () => {
    setIsLoading(true);
    // Reset alleen generatie-gerelateerde berichten, niet laadfouten
    // setError('');
    // setSuccess('');
    try {
      const response = await getInvoices();
      setInvoices(response.data);
    } catch (err) {
      console.error("Error fetching invoices:", err);
      setError('Kon facturen niet laden.');
    } finally {
      setIsLoading(false);
    }
  };

  // Haal data op bij mount
  useEffect(() => {
    fetchInvoices();
  }, []);

  // Functie om factuur generatie te triggeren
  const handleGenerateInvoices = async () => {
    setIsGenerating(true);
    setError('');
    setSuccess('');
    try {
      // Voeg hier eventueel parameters toe, bv. maand/jaar
      const response = await generateInvoices({ period: 'last_month' }); // Voorbeeld parameter
      setSuccess(response.data.message || 'Factuur generatie gestart/voltooid.');
      // Haal de lijst opnieuw op om nieuwe facturen te zien
      fetchInvoices();
    } catch (err) {
      console.error("Error generating invoices:", err);
      setError(err.response?.data?.error || 'Kon facturen niet genereren.');
    } finally {
      setIsGenerating(false);
    }
  };

   // Helper om datum te formatteren
   const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
        return new Date(dateString).toLocaleDateString('nl-NL', {
            year: 'numeric', month: 'numeric', day: 'numeric'
        });
    } catch (e) {
        return dateString; // Fallback
    }
   };

   // Helper om bedrag te formatteren
   const formatCurrency = (amount) => {
     if (amount === null || amount === undefined) return '';
     return new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR' }).format(amount);
   };

  return (
    <Box sx={{ maxWidth: '1000px', margin: 'auto' }}>
      <Typography variant="h4" gutterBottom component="h1">
        Facturen Overzicht
      </Typography>

      {/* Sectie voor genereren */}
      <Paper sx={{ p: 2, mb: 4 }} elevation={3}>
        <Typography variant="h6" gutterBottom>
          Facturen Genereren
        </Typography>
        {/* Toon berichten gerelateerd aan generatie */}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        <Button
          variant="contained"
          onClick={handleGenerateInvoices}
          disabled={isGenerating || isLoading} // Disable ook tijdens laden lijst
          startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : null}
        >
          {isGenerating ? 'Bezig...' : 'Genereer Maandelijkse Facturen'}
        </Button>
         <Typography variant="body2" sx={{mt: 1, fontStyle: 'italic'}}>
            (Dit genereert facturen voor nog niet gefactureerde behandelingen - implementatie in backend nodig)
         </Typography>
      </Paper>

      {/* Sectie voor lijst van facturen */}
      <Typography variant="h5" gutterBottom>
        Bestaande Facturen
      </Typography>
      {/* Toon laadfout alleen als het niet om een generatiefout gaat */}
       {error && !isGenerating && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      ) : invoices.length === 0 ? (
        <Typography sx={{ mt: 2 }}>Geen facturen gevonden.</Typography>
      ) : (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table sx={{ minWidth: 750 }} aria-label="invoices table">
            <TableHead>
              <TableRow>
                <TableCell>Factuurnr.</TableCell>
                <TableCell>Cliënt</TableCell>
                <TableCell>Factuurdatum</TableCell>
                <TableCell align="right">Totaalbedrag</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Acties</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell component="th" scope="row">
                    {invoice.invoice_number}
                  </TableCell>
                  <TableCell>{clients.name || 'N/A'}</TableCell> {/* Client naam uit backend halen */}
                  <TableCell>{formatDate(invoice.invoice_date)}</TableCell>
                  <TableCell align="right">{formatCurrency(invoice.total_amount)}</TableCell>
                  <TableCell>{invoice.status}</TableCell>
                  <TableCell align="center">
                    {/* Download knoppen */}
                    <IconButton
                      aria-label="download pdf"
                      color="primary"
                      component={Link} // Gebruik Link component voor href
                      href={getInvoicePdfUrl(invoice.id)} // Haal URL op uit API service
                      target="_blank" // Open in nieuw tabblad
                      rel="noopener noreferrer" // Veiligheid
                    >
                      <PictureAsPdfIcon />
                    </IconButton>
                    <IconButton
                      aria-label="download xls"
                      color="primary"
                      component={Link}
                      href={getInvoiceXlsUrl(invoice.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <DescriptionIcon /> {/* Of specifiek Excel icoon */}
                    </IconButton>
                     {/* Hier kan later nog een "Markeer als betaald" knop */}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

export default InvoicesPage;


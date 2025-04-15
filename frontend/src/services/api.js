import axios from 'axios';

// Gebruik de environment variable die Render injecteert tijdens de build,
// of val terug op localhost voor development.
const API_URL = process.env.REACT_APP_API_URL || 'https://lijf-leven-administratie-backend/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Client Functies ---
export const getClients = () => apiClient.get('/clients');
export const addClient = (clientData) => apiClient.post('/clients', clientData);
// Voeg hier PUT / DELETE toe indien nodig

// --- Treatment Method Functies ---
export const getTreatmentMethods = () => apiClient.get('/treatment-methods');
export const addTreatmentMethod = (methodData) => apiClient.post('/treatment-methods', methodData);
// Voeg hier PUT / DELETE toe indien nodig

// --- Treatment Functies ---
export const getTreatments = () => apiClient.get('/treatments');
export const addTreatment = (treatmentData) => apiClient.post('/treatments', treatmentData);
// Voeg hier PUT / DELETE toe indien nodig

// --- Invoice Functies ---
export const getInvoices = () => apiClient.get('/invoices');
export const generateInvoices = (params) => apiClient.post('/invoices/generate', params);
// Functies om download links te maken (geen directe API call, maar link naar endpoint)
export const getInvoicePdfUrl = (invoiceId) => `${API_URL}/invoices/${invoiceId}/pdf`;
export const getInvoiceXlsUrl = (invoiceId) => `${API_URL}/invoices/${invoiceId}/xls`;

export default apiClient;



// frontend/src/index.js

import React from 'react';
import ReactDOM from 'react-dom/client'; // Nieuwe import voor React 18+
import './index.css'; // Importeer eventuele globale CSS stijlen
import App from './App'; // Importeer je hoofd applicatie component
//import reportWebVitals from './reportWebVitals'; // Optioneel: voor performance meting

// Importeer CssBaseline van Material UI voor consistente styling basis
import CssBaseline from '@mui/material/CssBaseline';

// Zoek het root DOM element waar de app in gemount wordt (uit public/index.html)
const rootElement = document.getElementById('root');

// Maak een React root aan met de nieuwe API
const root = ReactDOM.createRoot(rootElement);

// Render de applicatie in de root
root.render(
  <React.StrictMode>
    {/* CssBaseline zorgt voor een goede, consistente basis over verschillende browsers */}
    <CssBaseline />
    {/* <App /> is je hoofdcomponent die de rest van de applicatie bevat (incl. routing) */}
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// Dit is optioneel en kan worden verwijderd als je het niet gebruikt.
//reportWebVitals();


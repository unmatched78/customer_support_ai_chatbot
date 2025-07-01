import React from 'react';
import { ClerkProvider } from '@clerk/clerk-react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import AdminDashboard from './components/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3b82f6',
    },
    secondary: {
      main: '#8b5cf6',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Use the exact key provided by the user
const clerkPubKey = "";

function App() {
  console.log("Using Clerk Publishable Key:", clerkPubKey);

  return (
    <ClerkProvider
      publishableKey={clerkPubKey}
      appearance={{
        elements: {
          formButtonPrimary: {
            backgroundColor: '#3b82f6',
            '&:hover': {
              backgroundColor: '#2563eb'
            }
          }
        }
      }}
    >
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <ChatInterface />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </ClerkProvider>
  );
}

export default App;
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignUp from './pages/SignUp';
import Login from './pages/Login';
import Home from './pages/Home';

// Protected Route Guard
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('smartagri_token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

// Auto-Redirect if logged in
const AuthRoute = ({ children }) => {
  const token = localStorage.getItem('smartagri_token');
  if (token) return <Navigate to="/home" replace />;
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <div className="bg-gray-100 min-h-screen text-[var(--text-900)]">
        <Routes>
          <Route path="/" element={<Navigate to="/signup" replace />} />
          
          <Route 
            path="/signup" 
            element={
              <AuthRoute>
                <SignUp />
              </AuthRoute>
            } 
          />
          
          <Route 
            path="/login" 
            element={
              <AuthRoute>
                <Login />
              </AuthRoute>
            } 
          />
          
          <Route 
            path="/home" 
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            } 
          />

          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

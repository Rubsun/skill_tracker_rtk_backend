import React from 'react';

// Create a context with a default value (usually null or an empty object)
// The actual value will be provided by the AuthProvider in App.jsx
export const AuthContext = React.createContext({
  user: null, // Structure: { token: string, role: 'employee' | 'manager', name: string } | null
  login: async (email, password) => {},
  register: async (email, name, password, role) => {},
  logout: () => {},
});


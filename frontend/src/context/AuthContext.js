import React, { createContext, useState, useEffect } from 'react';
import { getToken, removeToken } from '../utils/storage';
import api from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/user/profile/');
      const userData = response.data.data.user || {
        id: response.data.data.id,
        username: response.data.data.username,
        email: response.data.data.email,
      };
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      removeToken();
      setIsAuthenticated(false);
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, tokens) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  };

  const register = (userData, tokens) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    removeToken();
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loading,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

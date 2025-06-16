import React, { useContext, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const HomePage = () => {
    const { user } = useContext(AuthContext);

    // Wait for user context to be potentially loaded from storage
    if (user === undefined) { // Check if context is still initializing (if using async loading)
        return <div className="flex justify-center items-center h-screen"><LoadingSpinner /></div>;
    }

    if (!user) {
        // Should be handled by ProtectedRoute, but redirect just in case
        return <Navigate to="/login" replace />;
    }

    // Redirect based on user role
    if (user.role === 'manager') {
        return <Navigate to="/manager/dashboard" replace />;
    } else if (user.role === 'employee') {
        return <Navigate to="/employee/dashboard" replace />;
    } else {
        // Fallback if role is unknown or invalid - maybe logout or show error
        console.error("Unknown user role:", user.role);
        // For now, redirect to login
         return <Navigate to="/login" replace />;
    }

    // This part should not be reached
    return <div className="p-6">Redirecting...</div>;
};

export default HomePage;


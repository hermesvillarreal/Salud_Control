import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FoodLog from './pages/FoodLog';
import ExerciseLog from './pages/ExerciseLog';
import ClinicalDocs from './pages/ClinicalDocs';
import Calculators from './pages/Calculators';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import api from './services/api';

function App() {
    useEffect(() => {
        // Petición silenciosa para despertar el backend
        const wakeUpBackend = async () => {
            try {
                await api.get('/health');
                console.log('Backend despertado exitosamente');
            } catch (error) {
                console.error('Error al despertar el backend:', error);
            }
        };

        wakeUpBackend();
    }, []);

    return (
        <Router>
            <Routes>
                {/* Rutas de autenticación */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Rutas Protegidas */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/food-log" element={<FoodLog />} />
                    <Route path="/exercise-log" element={<ExerciseLog />} />
                    <Route path="/documents" element={<ClinicalDocs />} />
                    <Route path="/calculators" element={<Calculators />} />
                </Route>

                {/* Redirección por defecto */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* Fallback para 404 - redirige a dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Router>
    )
}

export default App

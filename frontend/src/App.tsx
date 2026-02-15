import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FoodLog from './pages/FoodLog';
import ClinicalDocs from './pages/ClinicalDocs';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <Router>
            <Routes>
                {/* Ruta de autenticación */}
                <Route path="/login" element={<Login />} />

                {/* Rutas Protegidas */}
                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/food-log" element={<FoodLog />} />
                    <Route path="/documents" element={<ClinicalDocs />} />
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

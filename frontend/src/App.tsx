import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FoodLog from './pages/FoodLog';
import ExerciseLog from './pages/ExerciseLog';
import ClinicalDocs from './pages/ClinicalDocs';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
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

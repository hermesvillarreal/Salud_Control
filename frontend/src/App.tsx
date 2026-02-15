import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FoodLog from './pages/FoodLog';

function App() {
    return (
        <Router>
            <Routes>
                {/* Dashboard principal */}
                <Route path="/dashboard" element={<Dashboard />} />

                {/* Registro de comida */}
                <Route path="/food-log" element={<FoodLog />} />

                {/* Redirección por defecto */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* Fallback para 404 - por ahora redirige a dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Router>
    )
}

export default App

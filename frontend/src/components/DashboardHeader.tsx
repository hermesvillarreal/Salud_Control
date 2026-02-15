import React from 'react';
import { Plus, Utensils, Scale, Activity, Droplets, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface DashboardHeaderProps {
    onRegisterPeso: () => void;
    onRegisterPresion: () => void;
    onRegisterGlucosa: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onRegisterPeso, onRegisterPresion, onRegisterGlucosa }) => {
    const navigate = useNavigate();
    const logout = useAuthStore((state) => state.logout);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="flex items-center justify-between w-full md:w-auto">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Panel de Control</h1>
                    <p className="text-slate-500">Bienvenido de nuevo. Aquí tienes un resumen de tu salud hoy.</p>
                </div>
                <button
                    onClick={handleLogout}
                    className="md:hidden p-2 text-slate-400 hover:text-red-600 transition-colors"
                    title="Cerrar Sesión"
                >
                    <LogOut className="w-6 h-6" />
                </button>
            </div>
            <div className="flex flex-wrap gap-2">
                <button
                    onClick={onRegisterPeso}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                >
                    <Scale className="w-4 h-4" />
                    <span>Registrar Peso</span>
                </button>
                <button
                    onClick={() => navigate('/food-log')}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                >
                    <Utensils className="w-4 h-4" />
                    <span>Registrar Comida</span>
                </button>
                <button
                    onClick={onRegisterPresion}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                >
                    <Activity className="w-4 h-4" />
                    <span>Presión Arterial</span>
                </button>
                <button
                    onClick={onRegisterGlucosa}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                >
                    <Droplets className="w-4 h-4" />
                    <span>Glucosa</span>
                </button>
                <button
                    onClick={handleLogout}
                    className="hidden md:flex items-center gap-2 bg-slate-100 hover:bg-red-50 text-slate-600 hover:text-red-600 px-4 py-2 rounded-xl font-medium transition-colors border border-slate-200"
                >
                    <LogOut className="w-4 h-4" />
                    <span>Salir</span>
                </button>
            </div>
        </div>
    );
};

export default DashboardHeader;

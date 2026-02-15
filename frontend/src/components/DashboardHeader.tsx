import React from 'react';
import { Plus, Utensils, Scale, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DashboardHeader: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Panel de Control</h1>
                <p className="text-slate-500">Bienvenido de nuevo, Hermes. Aquí tienes un resumen de tu salud hoy.</p>
            </div>
            <div className="flex flex-wrap gap-2">
                <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm">
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
                <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm">
                    <Activity className="w-4 h-4" />
                    <span>Presión/Glucosa</span>
                </button>
            </div>
        </div>
    );
};

export default DashboardHeader;

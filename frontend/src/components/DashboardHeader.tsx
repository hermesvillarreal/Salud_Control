import React, { useState, useRef, useEffect } from 'react';
import { Plus, Utensils, Scale, Activity, Droplets, LogOut, MessageSquare, X, Dumbbell, Calculator, FileText, CalendarDays, Menu as MenuIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface DashboardHeaderProps {
    onRegisterPeso: () => void;
    onRegisterPresion: () => void;
    onRegisterGlucosa: () => void;
    onOpenTelegram: () => void;
    isTelegramLinked: boolean;
    onUnlinkTelegram: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({
    onRegisterPeso,
    onRegisterPresion,
    onRegisterGlucosa,
    onOpenTelegram,
    isTelegramLinked,
    onUnlinkTelegram
}) => {
    const navigate = useNavigate();
    const logout = useAuthStore((state) => state.logout);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleMenuClick = (action: () => void) => {
        action();
        setIsMenuOpen(false);
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
            <div className="flex items-center gap-2">
                <div className="relative" ref={menuRef}>
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                    >
                        <Plus className="w-5 h-5" />
                        <span>Acciones</span>
                    </button>

                    {isMenuOpen && (
                        <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-100 py-2 z-50">
                            <button
                                onClick={() => handleMenuClick(() => navigate('/food-log'))}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-green-100 text-green-600 rounded-lg"><Utensils className="w-4 h-4" /></div>
                                <span className="font-medium">Comida</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(() => navigate('/exercise-log'))}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-orange-100 text-orange-600 rounded-lg"><Dumbbell className="w-4 h-4" /></div>
                                <span className="font-medium">Ejercicio</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(onRegisterGlucosa)}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-purple-100 text-purple-600 rounded-lg"><Droplets className="w-4 h-4" /></div>
                                <span className="font-medium">Glucosa</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(onRegisterPresion)}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-red-100 text-red-600 rounded-lg"><Activity className="w-4 h-4" /></div>
                                <span className="font-medium">Presión Arterial</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(onRegisterPeso)}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg"><Scale className="w-4 h-4" /></div>
                                <span className="font-medium">Peso</span>
                            </button>
                            <div className="h-px bg-slate-100 my-1"></div>
                            <button
                                onClick={() => handleMenuClick(() => navigate('/calculators'))}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg"><Calculator className="w-4 h-4" /></div>
                                <span className="font-medium">Calculadoras</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(() => navigate('/documents'))}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-teal-100 text-teal-600 rounded-lg"><FileText className="w-4 h-4" /></div>
                                <span className="font-medium">Documentos</span>
                            </button>
                            <button
                                onClick={() => handleMenuClick(() => navigate('/appointments'))}
                                className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 text-slate-700 transition-colors"
                            >
                                <div className="p-1.5 bg-pink-100 text-pink-600 rounded-lg"><CalendarDays className="w-4 h-4" /></div>
                                <span className="font-medium">Citas Médicas</span>
                            </button>
                        </div>
                    )}
                </div>

                {isTelegramLinked ? (
                    <button
                        onClick={onUnlinkTelegram}
                        className="flex items-center gap-2 bg-red-100 hover:bg-red-200 text-red-600 px-4 py-2 rounded-xl font-medium transition-colors border border-red-200"
                    >
                        <X className="w-4 h-4" />
                        <span className="hidden sm:inline">Desvincular Bot</span>
                    </button>
                ) : (
                    <button
                        onClick={onOpenTelegram}
                        className="flex items-center gap-2 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span className="hidden sm:inline">Bot Telegram</span>
                    </button>
                )}
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

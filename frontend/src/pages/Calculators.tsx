import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TDEECalculator from '../components/calculators/TDEECalculator';
import MacroCalculator from '../components/calculators/MacroCalculator';
import BMICalculator from '../components/calculators/BMICalculator';
import ASCVDCalculator from '../components/calculators/ASCVDCalculator';
import RCCCalculator from '../components/calculators/RCCCalculator';
import CalculatorHistory from '../components/calculators/CalculatorHistory';

type CalculatorTab = 'tdee' | 'macro' | 'bmi' | 'ascvd' | 'rcc' | 'history';

export default function Calculators() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<CalculatorTab>('tdee');
    const [refreshHistory, setRefreshHistory] = useState(0);

    const handleCalculationSaved = () => {
        setRefreshHistory(prev => prev + 1);
    };

    const tabs = [
        { id: 'tdee' as CalculatorTab, label: 'TDEE', icon: '🔥' },
        { id: 'macro' as CalculatorTab, label: 'Macros', icon: '🍽️' },
        { id: 'bmi' as CalculatorTab, label: 'BMI', icon: '⚖️' },
        { id: 'rcc' as CalculatorTab, label: 'RCC', icon: '📏' },
        { id: 'ascvd' as CalculatorTab, label: 'Riesgo Cardiovascular', icon: '❤️' },
        { id: 'history' as CalculatorTab, label: 'Historial', icon: '📊' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors mb-6 group"
                    >
                        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        <span className="font-medium">Volver al Panel</span>
                    </button>

                    <div>
                        <h1 className="text-4xl font-bold text-gray-800 mb-2">Calculadoras de Salud</h1>
                        <p className="text-gray-600">Herramientas basadas en fórmulas médicas validadas</p>
                    </div>
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-lg shadow-md mb-6 overflow-hidden">
                    <div className="flex border-b overflow-x-auto">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex-1 min-w-max px-6 py-4 font-medium transition-colors ${activeTab === tab.id
                                    ? 'bg-indigo-600 text-white border-b-4 border-indigo-700'
                                    : 'text-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                <span className="mr-2">{tab.icon}</span>
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    <div className="p-6">
                        {activeTab === 'tdee' && <TDEECalculator onSaved={handleCalculationSaved} />}
                        {activeTab === 'macro' && <MacroCalculator onSaved={handleCalculationSaved} />}
                        {activeTab === 'bmi' && <BMICalculator onSaved={handleCalculationSaved} />}
                        {activeTab === 'rcc' && <RCCCalculator onSaved={handleCalculationSaved} />}
                        {activeTab === 'ascvd' && <ASCVDCalculator onSaved={handleCalculationSaved} />}
                        {activeTab === 'history' && <CalculatorHistory key={refreshHistory} />}
                    </div>
                </div>

                {/* Disclaimer */}
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-yellow-700">
                                <strong>Aviso Importante:</strong> Estas calculadoras son herramientas educativas basadas en fórmulas médicas estándar.
                                Los resultados no reemplazan el consejo médico profesional. Consulte siempre con un profesional de la salud antes de
                                hacer cambios significativos en su dieta, ejercicio o tratamiento médico.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

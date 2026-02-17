import { useState, useEffect } from 'react';
import api from '../../services/api';

interface CalculatorRecord {
    id: number;
    calculator_type: string;
    fecha_hora: string;
    input_data: any;
    result_data: any;
    notes: string | null;
}

export default function CalculatorHistory() {
    const [history, setHistory] = useState<CalculatorRecord[]>([]);
    const [filter, setFilter] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [selectedRecord, setSelectedRecord] = useState<CalculatorRecord | null>(null);

    useEffect(() => {
        fetchHistory();
    }, [filter]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const url = filter ? `/calculators/history?calculator_type=${filter}` : '/calculators/history';
            const response = await api.get(url);
            setHistory(response.data);
        } catch (error) {
            console.error('Error fetching history:', error);
        } finally {
            setLoading(false);
        }
    };

    const getCalculatorLabel = (type: string) => {
        const labels: Record<string, string> = {
            tdee: 'TDEE',
            macro: 'Macros',
            bmi: 'IMC',
            ascvd: 'Riesgo Cardiovascular',
        };
        return labels[type] || type;
    };

    const getCalculatorIcon = (type: string) => {
        const icons: Record<string, string> = {
            tdee: '🔥',
            macro: '🍽️',
            bmi: '⚖️',
            ascvd: '❤️',
        };
        return icons[type] || '📊';
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const renderResultSummary = (type: string, result: any) => {
        switch (type) {
            case 'tdee':
                return `TDEE: ${result.tdee?.toLocaleString()} kcal/día`;
            case 'macro':
                return `${result.protein_g}g P / ${result.carbs_g}g C / ${result.fat_g}g G`;
            case 'bmi':
                return `IMC: ${result.bmi} (${result.category})`;
            case 'ascvd':
                return `Riesgo: ${result.risk_percentage}% (${result.risk_category})`;
            default:
                return 'Ver detalles';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Historial de Cálculos</h2>
                    <p className="text-gray-600">Revisa tus cálculos anteriores</p>
                </div>

                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                    <option value="">Todos</option>
                    <option value="tdee">TDEE</option>
                    <option value="macro">Macros</option>
                    <option value="bmi">IMC</option>
                    <option value="ascvd">Riesgo Cardiovascular</option>
                </select>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                    <p className="text-gray-600 mt-4">Cargando historial...</p>
                </div>
            ) : history.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg">
                    <p className="text-gray-600">No hay cálculos guardados aún</p>
                    <p className="text-sm text-gray-500 mt-2">Usa las calculadoras para comenzar</p>
                </div>
            ) : (
                <div className="grid gap-4">
                    {history.map((record) => (
                        <div
                            key={record.id}
                            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
                            onClick={() => setSelectedRecord(record)}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-start space-x-3">
                                    <span className="text-3xl">{getCalculatorIcon(record.calculator_type)}</span>
                                    <div>
                                        <h3 className="font-semibold text-gray-800">
                                            {getCalculatorLabel(record.calculator_type)}
                                        </h3>
                                        <p className="text-sm text-gray-600">{formatDate(record.fecha_hora)}</p>
                                        <p className="text-sm text-indigo-600 mt-1">
                                            {renderResultSummary(record.calculator_type, record.result_data)}
                                        </p>
                                    </div>
                                </div>
                                <button className="text-indigo-600 hover:text-indigo-800">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Detail Modal */}
            {selectedRecord && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-800">
                                        {getCalculatorIcon(selectedRecord.calculator_type)} {getCalculatorLabel(selectedRecord.calculator_type)}
                                    </h3>
                                    <p className="text-sm text-gray-600">{formatDate(selectedRecord.fecha_hora)}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedRecord(null)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h4 className="font-semibold text-gray-800 mb-2">Datos de Entrada</h4>
                                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                                        {JSON.stringify(selectedRecord.input_data, null, 2)}
                                    </pre>
                                </div>

                                <div className="bg-indigo-50 p-4 rounded-lg">
                                    <h4 className="font-semibold text-gray-800 mb-2">Resultados</h4>
                                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                                        {JSON.stringify(selectedRecord.result_data, null, 2)}
                                    </pre>
                                </div>

                                {selectedRecord.notes && (
                                    <div className="bg-yellow-50 p-4 rounded-lg">
                                        <h4 className="font-semibold text-gray-800 mb-2">Notas</h4>
                                        <p className="text-sm text-gray-700">{selectedRecord.notes}</p>
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={() => setSelectedRecord(null)}
                                className="mt-6 w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

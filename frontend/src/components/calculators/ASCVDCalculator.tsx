import { useState } from 'react';
import api from '../../services/api';
import { getLocalISOString } from '../../utils/dateUtils';

interface ASCVDResult {
    risk_percentage: number;
    risk_category: string;
    recommendation: string;
    error?: string;
}

interface Props {
    onSaved?: () => void;
}

export default function ASCVDCalculator({ onSaved }: Props) {
    const [age, setAge] = useState('');
    const [gender, setGender] = useState('male');
    const [race, setRace] = useState('white');
    const [totalChol, setTotalChol] = useState('');
    const [hdl, setHdl] = useState('');
    const [systolicBP, setSystolicBP] = useState('');
    const [isDiabetic, setIsDiabetic] = useState(false);
    const [isSmoker, setIsSmoker] = useState(false);
    const [onBPMeds, setOnBPMeds] = useState(false);
    const [result, setResult] = useState<ASCVDResult | null>(null);
    const [loading, setLoading] = useState(false);

    const handleCalculate = async () => {
        if (!age || !totalChol || !hdl || !systolicBP) {
            alert('Por favor completa todos los campos requeridos');
            return;
        }

        const ageNum = parseInt(age);
        if (ageNum < 40 || ageNum > 79) {
            alert('La calculadora ASCVD es válida para edades entre 40-79 años');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/calculators/ascvd', {
                age: ageNum,
                gender,
                race,
                total_cholesterol: parseFloat(totalChol),
                hdl_cholesterol: parseFloat(hdl),
                systolic_bp: parseInt(systolicBP),
                is_diabetic: isDiabetic,
                is_smoker: isSmoker,
                on_bp_medication: onBPMeds,
                fecha_hora: getLocalISOString(),
            });

            setResult(response.data.result);
            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error calculating ASCVD:', error);
            alert('Error al calcular riesgo ASCVD');
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (risk: number) => {
        if (risk < 5) return 'text-green-600';
        if (risk < 7.5) return 'text-yellow-600';
        if (risk < 20) return 'text-orange-600';
        return 'text-red-600';
    };

    const getRiskBgColor = (risk: number) => {
        if (risk < 5) return 'bg-green-50';
        if (risk < 7.5) return 'bg-yellow-50';
        if (risk < 20) return 'bg-orange-50';
        return 'bg-red-50';
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Calculadora de Riesgo Cardiovascular (ASCVD)</h2>
                <p className="text-gray-600">
                    Estima el riesgo a 10 años de enfermedad cardiovascular aterosclerótica (ACC/AHA 2013)
                </p>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-4">
                <p className="text-sm text-yellow-800">
                    <strong>⚠️ Importante:</strong> Esta calculadora es válida para personas de 40-79 años sin enfermedad cardiovascular conocida.
                    Los resultados deben ser interpretados por un profesional de la salud.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Edad (años)</label>
                            <input
                                type="number"
                                value={age}
                                onChange={(e) => setAge(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                placeholder="50"
                            />
                            <p className="text-xs text-gray-500 mt-1">40-79 años</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
                            <select
                                value={gender}
                                onChange={(e) => setGender(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            >
                                <option value="male">Masculino</option>
                                <option value="female">Femenino</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Raza</label>
                        <select
                            value={race}
                            onChange={(e) => setRace(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value="white">Caucásico / Otro</option>
                            <option value="black">Afroamericano</option>
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Colesterol Total (mg/dL)</label>
                            <input
                                type="number"
                                value={totalChol}
                                onChange={(e) => setTotalChol(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                placeholder="200"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">HDL (mg/dL)</label>
                            <input
                                type="number"
                                value={hdl}
                                onChange={(e) => setHdl(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                placeholder="50"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Presión Sistólica (mmHg)</label>
                        <input
                            type="number"
                            value={systolicBP}
                            onChange={(e) => setSystolicBP(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="120"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={isDiabetic}
                                onChange={(e) => setIsDiabetic(e.target.checked)}
                                className="mr-3 h-5 w-5 text-indigo-600 rounded"
                            />
                            <span className="text-gray-700">Diabetes</span>
                        </label>

                        <label className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={isSmoker}
                                onChange={(e) => setIsSmoker(e.target.checked)}
                                className="mr-3 h-5 w-5 text-indigo-600 rounded"
                            />
                            <span className="text-gray-700">Fumador actual</span>
                        </label>

                        <label className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={onBPMeds}
                                onChange={(e) => setOnBPMeds(e.target.checked)}
                                className="mr-3 h-5 w-5 text-indigo-600 rounded"
                            />
                            <span className="text-gray-700">Tratamiento para hipertensión</span>
                        </label>
                    </div>

                    <button
                        onClick={handleCalculate}
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
                    >
                        {loading ? 'Calculando...' : 'Calcular Riesgo'}
                    </button>
                </div>

                {/* Results */}
                {result && !result.error && (
                    <div className={`${getRiskBgColor(result.risk_percentage!)} p-6 rounded-lg`}>
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Resultado del Riesgo</h3>

                        <div className="space-y-4">
                            <div className="bg-white p-6 rounded-lg shadow text-center">
                                <div className="text-sm text-gray-600 mb-2">Riesgo a 10 años</div>
                                <div className={`text-6xl font-bold ${getRiskColor(result.risk_percentage!)}`}>
                                    {result.risk_percentage}%
                                </div>
                                <div className="text-lg font-semibold text-gray-800 mt-3">{result.risk_category}</div>
                            </div>

                            {/* Risk Scale */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="text-sm font-medium text-gray-700 mb-2">Escala de Riesgo</div>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between items-center">
                                        <span className="text-green-600">Bajo riesgo</span>
                                        <span className="text-gray-600">&lt; 5%</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-yellow-600">Riesgo limítrofe</span>
                                        <span className="text-gray-600">5% - 7.4%</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-orange-600">Riesgo intermedio</span>
                                        <span className="text-gray-600">7.5% - 19.9%</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-red-600">Alto riesgo</span>
                                        <span className="text-gray-600">≥ 20%</span>
                                    </div>
                                </div>
                            </div>

                            {/* Recommendation */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <h4 className="font-semibold text-gray-800 mb-2">Recomendación</h4>
                                <p className="text-sm text-gray-700">{result.recommendation}</p>
                            </div>

                            <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded text-sm text-red-800">
                                <strong>⚠️ Importante:</strong> Este resultado debe ser discutido con tu médico.
                                Factores adicionales pueden influir en tu riesgo real y opciones de tratamiento.
                            </div>
                        </div>
                    </div>
                )}

                {result && result.error && (
                    <div className="bg-red-50 p-6 rounded-lg">
                        <p className="text-red-800">{result.error}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

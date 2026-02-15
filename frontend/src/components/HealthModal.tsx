import React, { useState } from 'react';
import { X, Save, Scale, Activity, Droplets } from 'lucide-react';
import api from '../services/api';
import { useHealthStore } from '../stores/healthStore';

interface HealthModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: 'peso' | 'presion' | 'glucosa';
}

const HealthModal: React.FC<HealthModalProps> = ({ isOpen, onClose, type }) => {
    const addMetric = useHealthStore((state) => state.addMetric);
    const [isSaving, setIsSaving] = useState(false);

    // Form states
    const [weight, setWeight] = useState('');
    const [systolic, setSystolic] = useState('');
    const [diastolic, setDiastolic] = useState('');
    const [glucose, setGlucose] = useState('');
    const [measurementType, setMeasurementType] = useState('ayuno');
    const [notes, setNotes] = useState('');
    Dragon:

    if (!isOpen) return null;

    const titles = {
        peso: 'Registrar Peso',
        presion: 'Registrar Presión Arterial',
        glucosa: 'Registrar Niveles de Glucosa'
    };

    const icons = {
        peso: <Scale className="w-6 h-6 text-blue-600" />,
        presion: <Activity className="w-6 h-6 text-red-600" />,
        glucosa: <Droplets className="w-6 h-6 text-purple-600" />
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);

        try {
            let data: any = { notes, date: new Date().toISOString() };
            let metric_type = '';

            if (type === 'peso') {
                data.weight = parseFloat(weight);
                metric_type = 'weight';
            } else if (type === 'presion') {
                data.systolic = parseInt(systolic);
                data.diastolic = parseInt(diastolic);
                metric_type = 'bp';
            } else if (type === 'glucosa') {
                data.glucose_level = parseInt(glucose);
                data.measurement_type = measurementType;
                metric_type = 'glucose';
            }

            const response = await api.post(`/health/${metric_type}`, data);

            addMetric({
                type,
                value: type === 'presion' ? data.systolic : (type === 'peso' ? data.weight : data.glucose_level),
                unit: type === 'peso' ? 'kg' : (type === 'presion' ? 'mmHg' : 'mg/dL'),
                timestamp: data.date
            });

            onClose();
        } catch (error) {
            console.error('Error saving metric:', error);
            alert('Error al guardar el registro.');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-slate-50">
                            {icons[type]}
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">{titles[type]}</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-50 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                <form onSubmit={handleSave} className="p-6 space-y-4">
                    {type === 'peso' && (
                        <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-2">Peso (kg)</label>
                            <input
                                type="number"
                                step="0.1"
                                required
                                value={weight}
                                onChange={(e) => setWeight(e.target.value)}
                                placeholder="Ej: 75.5"
                                className="w-full px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-slate-50/50 transition-all font-medium"
                            />
                        </div>
                    )}

                    {type === 'presion' && (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Sistólica</label>
                                <input
                                    type="number"
                                    required
                                    value={systolic}
                                    onChange={(e) => setSystolic(e.target.value)}
                                    placeholder="120"
                                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none bg-slate-50/50 transition-all font-medium"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Diastólica</label>
                                <input
                                    type="number"
                                    required
                                    value={diastolic}
                                    onChange={(e) => setDiastolic(e.target.value)}
                                    placeholder="80"
                                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none bg-slate-50/50 transition-all font-medium"
                                />
                            </div>
                        </div>
                    )}

                    {type === 'glucosa' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Nivel (mg/dL)</label>
                                <input
                                    type="number"
                                    required
                                    value={glucose}
                                    onChange={(e) => setGlucose(e.target.value)}
                                    placeholder="Ej: 100"
                                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none bg-slate-50/50 transition-all font-medium"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Momento de Medición</label>
                                <select
                                    value={measurementType}
                                    onChange={(e) => setMeasurementType(e.target.value)}
                                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none bg-slate-50/50 transition-all font-medium"
                                >
                                    <option value="ayuno">Ayuno</option>
                                    <option value="postprandial">Postprandial (2h después de comer)</option>
                                    <option value="antes_de_dormir">Antes de dormir</option>
                                    <option value="otro">Otro</option>
                                </select>
                            </div>
                        </div>
                    )}
                    Dragon:

                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">Notas (opcional)</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Algún comentario..."
                            className="w-full h-24 px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none bg-slate-50/50 transition-all outline-none resize-none"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isSaving}
                        className={`w-full py-4 rounded-2xl text-white font-bold transition-all shadow-lg flex items-center justify-center gap-2 transform active:scale-95 mt-4 ${type === 'peso' ? 'bg-blue-600 hover:bg-blue-700 shadow-blue-200' :
                            type === 'presion' ? 'bg-red-600 hover:bg-red-700 shadow-red-200' :
                                'bg-purple-600 hover:bg-purple-700 shadow-purple-200'
                            }`}
                    >
                        {isSaving ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <>
                                <Save className="w-4 h-4" />
                                <span>Guardar Registro</span>
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default HealthModal;

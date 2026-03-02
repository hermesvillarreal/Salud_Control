import React, { useState, useEffect } from 'react';
import { CalendarDays, Plus, Info, Stethoscope, AlertCircle, FileSearch, Trash2, CheckCircle2, Circle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Prerequisite {
    id: number;
    description: string;
    prerequisite_type: 'lab' | 'exam' | 'document';
    is_completed: boolean;
    document_id: number | null;
}

interface Appointment {
    id: number;
    fecha_hora: string;
    doctor_name: string;
    specialty: string | null;
    reason: string;
    symptoms: string | null;
    diagnosis: string | null;
    location: string | null;
    phone_number: string | null;
    status: 'scheduled' | 'completed' | 'cancelled';
    notes: string | null;
    prerequisites: Prerequisite[];
}

const Appointments: React.FC = () => {
    const navigate = useNavigate();
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState(true);

    // Filter states
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [filterDateFrom, setFilterDateFrom] = useState<string>('');
    const [filterDateTo, setFilterDateTo] = useState<string>('');
    const [filterSearch, setFilterSearch] = useState<string>(''); // For doctor, specialty, location, phone

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAppo, setSelectedAppo] = useState<Appointment | null>(null);

    // Form states
    const [fechaHora, setFechaHora] = useState('');
    const [doctorName, setDoctorName] = useState('');
    const [specialty, setSpecialty] = useState('');
    const [reason, setReason] = useState('');
    const [symptoms, setSymptoms] = useState('');
    const [diagnosis, setDiagnosis] = useState('');
    const [location, setLocation] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [status, setStatus] = useState<'scheduled' | 'completed' | 'cancelled'>('scheduled');

    const [newPrereq, setNewPrereq] = useState('');
    const [prereqType, setPrereqType] = useState<'lab' | 'exam' | 'document'>('lab');

    const loadAppointments = async () => {
        try {
            setLoading(true);
            const response = await api.get('/appointments');
            const data = response.data;
            // The endpoint currently returns appointments, but we need to fetch their prerequisites
            // We modified the endpoint previously to include `prerequisites` in the individual GET, 
            // but let's fetch them all or assume we need to get details on demand.
            // Actually, the GET /appointments doesn't return prerequisites. Let's assume we do 
            // parallel fetches for now, or just show them in the detailed view.
            setAppointments(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    const openCreateModal = () => {
        setIsModalOpen(true);
        setSelectedAppo(null);
        setFechaHora('');
        setDoctorName('');
        setSpecialty('');
        setReason('');
        setSymptoms('');
        setDiagnosis('');
        setLocation('');
        setPhoneNumber('');
        setStatus('scheduled');
    };

    const openEditModal = async (appoId: number) => {
        try {
            const res = await api.get(`/appointments/${appoId}`);
            const appo = res.data;

            setSelectedAppo(appo);
            setFechaHora(appo.fecha_hora.slice(0, 16));
            setDoctorName(appo.doctor_name);
            setSpecialty(appo.specialty || '');
            setReason(appo.reason);
            setSymptoms(appo.symptoms || '');
            setDiagnosis(appo.diagnosis || '');
            setLocation(appo.location || '');
            setPhoneNumber(appo.phone_number || '');
            setStatus(appo.status);
            setIsModalOpen(true);
        } catch (error) {
            console.error(error);
        }
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const data = {
                fecha_hora: fechaHora,
                doctor_name: doctorName,
                specialty,
                reason,
                symptoms,
                diagnosis,
                location,
                phone_number: phoneNumber,
                status
            };

            if (selectedAppo) {
                await api.put(`/appointments/${selectedAppo.id}`, data);
            } else {
                await api.post('/appointments', data);
            }
            setIsModalOpen(false);
            loadAppointments();
        } catch (error) {
            alert('Error al guardar la cita');
            console.error(error);
        }
    };

    const handleAddPrerequisite = async () => {
        if (!selectedAppo || !newPrereq) return;
        try {
            await api.post(`/appointments/${selectedAppo.id}/prerequisites`, {
                description: newPrereq,
                prerequisite_type: prereqType,
            });
            setNewPrereq('');
            openEditModal(selectedAppo.id);
        } catch (error) {
            console.error(error);
        }
    };

    const handleTogglePrereq = async (req: Prerequisite) => {
        try {
            await api.put(`/prerequisites/${req.id}`, {
                is_completed: !req.is_completed
            });
            if (selectedAppo) openEditModal(selectedAppo.id);
        } catch (e) { console.error(e); }
    };

    const handleDeletePrereq = async (reqId: number) => {
        try {
            await api.delete(`/prerequisites/${reqId}`);
            if (selectedAppo) openEditModal(selectedAppo.id);
        } catch (e) { console.error(e); }
    };

    const handleAnalyzeDoc = async (docId: number) => {
        try {
            alert("Analizando documento... Esto puede tomar unos segundos.");
            const res = await api.post(`/documents/${docId}/analyze`);
            const aiData = res.data;
            alert(`Resumen:\n${aiData.summary}\n\nAviso:\n${aiData.ai_disclaimer}`);
        } catch (e) {
            console.error(e);
            alert("Error al analizar el documento");
        }
    };

    const filteredAppointments = appointments.filter(appo => {
        let match = true;

        if (filterStatus !== 'all' && appo.status !== filterStatus) {
            match = false;
        }

        if (filterDateFrom) {
            if (new Date(appo.fecha_hora) < new Date(filterDateFrom)) match = false;
        }
        if (filterDateTo) {
            // Include the entire end date by setting time to 23:59:59
            const toDate = new Date(filterDateTo);
            toDate.setHours(23, 59, 59, 999);
            if (new Date(appo.fecha_hora) > toDate) match = false;
        }

        if (filterSearch) {
            const searchLower = filterSearch.toLowerCase();
            const doctor = appo.doctor_name?.toLowerCase() || '';
            const specialty = appo.specialty?.toLowerCase() || '';
            const location = appo.location?.toLowerCase() || '';
            const phone = appo.phone_number?.toLowerCase() || '';
            const reason = appo.reason?.toLowerCase() || '';

            if (!doctor.includes(searchLower) &&
                !specialty.includes(searchLower) &&
                !location.includes(searchLower) &&
                !phone.includes(searchLower) &&
                !reason.includes(searchLower)) {
                match = false;
            }
        }

        return match;
    });

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header block */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
                            <CalendarDays className="w-8 h-8 text-pink-500" />
                            Citas y Laboratorios
                        </h1>
                        <p className="text-slate-500 mt-1">
                            Gestiona tus próximas citas, diagnósticos y requisitos previos.
                        </p>
                    </div>
                </div>

                <div className="mb-6 flex gap-2">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded-xl font-medium transition-colors"
                    >
                        Volver
                    </button>
                    <button
                        onClick={openCreateModal}
                        className="flex items-center gap-2 bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-sm"
                    >
                        <Plus className="w-5 h-5" />
                        Nueva Cita
                    </button>
                </div>

                {/* Filters */}
                <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 mb-6 flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                        <label className="block text-xs font-medium text-slate-500 mb-1">Buscar (Doctor, Especialidad, Lugar...)</label>
                        <input
                            type="text"
                            placeholder="Término de búsqueda"
                            value={filterSearch}
                            onChange={e => setFilterSearch(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                        />
                    </div>
                    <div className="w-full md:w-40">
                        <label className="block text-xs font-medium text-slate-500 mb-1">Estado</label>
                        <select
                            value={filterStatus}
                            onChange={e => setFilterStatus(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                        >
                            <option value="all">Todos</option>
                            <option value="scheduled">Programadas</option>
                            <option value="completed">Completadas</option>
                            <option value="cancelled">Canceladas</option>
                        </select>
                    </div>
                    <div className="w-full md:w-40">
                        <label className="block text-xs font-medium text-slate-500 mb-1">Desde</label>
                        <input
                            type="date"
                            value={filterDateFrom}
                            onChange={e => setFilterDateFrom(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                        />
                    </div>
                    <div className="w-full md:w-40">
                        <label className="block text-xs font-medium text-slate-500 mb-1">Hasta</label>
                        <input
                            type="date"
                            value={filterDateTo}
                            onChange={e => setFilterDateTo(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-10">Cargando citas...</div>
                ) : (
                    <div className="grid gap-4">
                        {filteredAppointments.length === 0 ? (
                            <div className="bg-white rounded-3xl p-12 text-center border border-slate-100">
                                <Stethoscope className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                                <h3 className="text-xl font-bold text-slate-800 mb-2">No se encontraron citas</h3>
                                <p className="text-slate-500">Intenta cambiar los filtros de búsqueda.</p>
                            </div>
                        ) : (
                            filteredAppointments.map(appo => (
                                <div
                                    key={appo.id}
                                    onClick={() => openEditModal(appo.id)}
                                    className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 cursor-pointer hover:shadow-md transition-shadow flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-l-4 border-l-pink-500"
                                >
                                    <div>
                                        <h3 className="font-bold text-slate-900 text-lg">{appo.doctor_name}</h3>
                                        <p className="text-slate-600 text-sm">{appo.specialty} • {appo.reason}</p>
                                        <div className="text-slate-500 text-xs mt-1 flex flex-col sm:flex-row sm:gap-4">
                                            {appo.location && <span>📍 {appo.location}</span>}
                                            {appo.phone_number && <span>📞 {appo.phone_number}</span>}
                                        </div>
                                        <p className="text-slate-400 text-xs mt-2">
                                            {new Date(appo.fecha_hora).toLocaleString('es-ES', { dateStyle: 'long', timeStyle: 'short' })}
                                        </p>
                                    </div>
                                    <div className="flex gap-2 items-center">
                                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider
                                            ${appo.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                                                appo.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                            {appo.status === 'scheduled' ? 'Programada' : appo.status === 'completed' ? 'Completada' : 'Cancelada'}
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* View / Edit Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setIsModalOpen(false)}></div>
                    <div className="relative bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl shadow-2xl p-6">
                        <h2 className="text-2xl font-bold mb-4">{selectedAppo ? 'Detalle de la Cita' : 'Nueva Cita'}</h2>

                        <form onSubmit={handleSave} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Fecha y Hora *</label>
                                    <input
                                        type="datetime-local"
                                        required
                                        value={fechaHora}
                                        onChange={e => setFechaHora(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Estado</label>
                                    <select
                                        value={status}
                                        onChange={e => setStatus(e.target.value as any)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                    >
                                        <option value="scheduled">Programada</option>
                                        <option value="completed">Completada</option>
                                        <option value="cancelled">Cancelada</option>
                                    </select>
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Doctor/Profesional *</label>
                                    <input
                                        type="text"
                                        required
                                        value={doctorName}
                                        onChange={e => setDoctorName(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Especialidad</label>
                                    <input
                                        type="text"
                                        value={specialty}
                                        onChange={e => setSpecialty(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Motivo / Tipo de Cita *</label>
                                    <input
                                        type="text"
                                        required
                                        value={reason}
                                        onChange={e => setReason(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Lugar de la Cita</label>
                                    <input
                                        type="text"
                                        value={location}
                                        onChange={e => setLocation(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                        placeholder="Ej: Clínica Centro, Consultorio 10"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Teléfono</label>
                                    <input
                                        type="tel"
                                        value={phoneNumber}
                                        onChange={e => setPhoneNumber(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                        placeholder="Para cancelar o contactar"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <h3 className="font-semibold text-slate-800 mt-4 border-b pb-2">Evaluación Médica</h3>
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Síntomas Previos</label>
                                    <textarea
                                        value={symptoms}
                                        onChange={e => setSymptoms(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                        rows={2}
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Diagnóstico / Indicaciones</label>
                                    <textarea
                                        value={diagnosis}
                                        onChange={e => setDiagnosis(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2"
                                        rows={2}
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-600 font-medium">Cancelar</button>
                                <button type="submit" className="bg-pink-600 text-white px-6 py-2 rounded-xl font-bold hover:bg-pink-700 transition">Guardar</button>
                            </div>
                        </form>

                        {/* Prerequisites Checklist rendering if Editing an existing Appointment */}
                        {selectedAppo && (
                            <div className="mt-8 border-t pt-6">
                                <h3 className="text-xl font-bold flex items-center gap-2 mb-4">
                                    <FileSearch className="w-5 h-5 text-indigo-500" />
                                    Requisitos Previos (Checklist)
                                </h3>

                                <div className="space-y-2 mb-6">
                                    {selectedAppo.prerequisites?.length === 0 ? (
                                        <p className="text-slate-400 text-sm">No hay requisitos para esta cita.</p>
                                    ) : (
                                        selectedAppo.prerequisites?.map(req => (
                                            <div key={req.id} className="flex items-center justify-between bg-slate-50 border p-3 rounded-lg">
                                                <div className="flex items-center gap-3">
                                                    <button onClick={() => handleTogglePrereq(req)} className="focus:outline-none">
                                                        {req.is_completed ? (
                                                            <CheckCircle2 className="w-6 h-6 text-green-500" />
                                                        ) : (
                                                            <Circle className="w-6 h-6 text-slate-300" />
                                                        )}
                                                    </button>
                                                    <div>
                                                        <p className={`font-medium ${req.is_completed ? 'line-through text-slate-400' : 'text-slate-800'}`}>
                                                            {req.description} ({req.prerequisite_type})
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {req.document_id && (
                                                        <button
                                                            onClick={() => handleAnalyzeDoc(req.document_id!)}
                                                            className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded hover:bg-indigo-200"
                                                        >
                                                            Analizar Doc (IA)
                                                        </button>
                                                    )}
                                                    <button onClick={() => handleDeletePrereq(req.id)} className="text-red-400 hover:text-red-600">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>

                                <div className="flex flex-col sm:flex-row gap-2">
                                    <input
                                        type="text"
                                        placeholder="Nuevo requisito (ej: Hemograma)"
                                        value={newPrereq}
                                        onChange={e => setNewPrereq(e.target.value)}
                                        className="flex-1 border rounded-lg px-3 py-2 text-sm"
                                    />
                                    <select value={prereqType} onChange={e => setPrereqType(e.target.value as any)} className="border rounded-lg px-3 py-2 text-sm">
                                        <option value="lab">Laboratorio</option>
                                        <option value="exam">Examen</option>
                                        <option value="document">Otro Doc</option>
                                    </select>
                                    <button onClick={handleAddPrerequisite} className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium text-sm">Agregar</button>
                                </div>

                                <div className="mt-6 bg-amber-50 rounded-xl p-4 flex gap-3 text-amber-800 text-sm">
                                    <AlertCircle className="w-5 h-5 shrink-0 text-amber-600" />
                                    <p>
                                        <strong>Aviso importante:</strong> El análisis de documentos con IA es una guía básica para que comprendas mejor tus resultados. <strong>Nunca</strong> sustituye la valoración médica profesional. Para decisiones terapéuticas, consulta únicamente con tu médico.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Appointments;

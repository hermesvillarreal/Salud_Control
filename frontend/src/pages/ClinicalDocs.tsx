import React, { useState, useEffect, useCallback } from 'react';
import {
    Upload, FileText, Beaker, FileSearch, Trash2,
    X, Maximize2, FilePlus, ChevronLeft, Download
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface ClinicalDocument {
    id: number;
    title: string;
    document_type: string;
    file_path: string;
    notes: string | null;
    date: string;
}

const ClinicalDocs: React.FC = () => {
    const navigate = useNavigate();
    const [documents, setDocuments] = useState<ClinicalDocument[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState<ClinicalDocument | null>(null);

    // Form state
    const [title, setTitle] = useState('');
    const [docType, setDocType] = useState('receta');
    const [notes, setNotes] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const fetchDocuments = async () => {
        try {
            const response = await api.get('/documents');
            setDocuments(response.data);
        } catch (error) {
            console.error("Error fetching documents:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            if (!title) setTitle(e.dataTransfer.files[0].name.split('.')[0]);
        }
    }, [title]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            if (!title) setTitle(e.target.files[0].name.split('.')[0]);
        }
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file || !title) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        formData.append('doc_type', docType);
        formData.append('notes', notes);

        try {
            await api.post('/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Reset form
            setTitle('');
            setDocType('receta');
            setNotes('');
            setFile(null);
            // Refresh list
            fetchDocuments();
        } catch (error) {
            console.error("Error uploading document:", error);
            alert("Error al subir el documento");
        } finally {
            setUploading(false);
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'receta': return <FileText className="w-6 h-6 text-blue-500" />;
            case 'laboratorio': return <Beaker className="w-6 h-6 text-green-500" />;
            case 'estudio': return <FileSearch className="w-6 h-6 text-purple-500" />;
            default: return <FileText className="w-6 h-6 text-slate-500" />;
        }
    };

    const getFullUrl = (path: string) => {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        // Normalize path (linux-style for web)
        const normalizedPath = path.replace(/\\/g, '/');
        return `${baseUrl}/${normalizedPath}`;
    };

    const isImage = (path: string) => {
        const ext = path.split('.').pop()?.toLowerCase();
        return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '');
    };

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="p-2 hover:bg-white rounded-full transition-colors shadow-sm"
                    >
                        <ChevronLeft className="w-6 h-6" />
                    </button>
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">Documentos Clínicos</h1>
                        <p className="text-slate-500">Gestiona tus recetas, análisis y estudios médicos</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Upload Section */}
                    <div className="lg:col-span-1">
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <FilePlus className="w-5 h-5 text-blue-600" />
                                Subir Nuevo Documento
                            </h2>

                            <form onSubmit={handleUpload} className="space-y-4">
                                <div
                                    className={`relative border-2 border-dashed rounded-xl p-8 transition-all text-center
                                        ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-slate-300'}
                                        ${file ? 'bg-slate-50' : ''}`}
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                >
                                    <input
                                        type="file"
                                        onChange={handleFileChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        accept="image/*,.pdf"
                                    />

                                    {!file ? (
                                        <div className="space-y-2">
                                            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                                <Upload className="w-6 h-6 text-blue-600" />
                                            </div>
                                            <p className="text-sm font-medium text-slate-700">Haz click o arrastra un archivo</p>
                                            <p className="text-xs text-slate-400">Imágenes o PDFs (Máx. 10MB)</p>
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-between bg-white p-2 rounded-lg border border-slate-200">
                                            <div className="flex items-center gap-2 overflow-hidden">
                                                <FileText className="w-5 h-5 text-blue-500 shrink-0" />
                                                <span className="text-sm font-medium truncate">{file.name}</span>
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => setFile(null)}
                                                className="p-1 hover:bg-red-50 text-red-500 rounded"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Título</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                        placeholder="Ej: Análisis Sangre Feb 2024"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Tipo de Documento</label>
                                    <select
                                        value={docType}
                                        onChange={(e) => setDocType(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                    >
                                        <option value="receta">Receta</option>
                                        <option value="laboratorio">Laboratorio</option>
                                        <option value="estudio">Estudio</option>
                                        <option value="imagen">Imagen Genérica</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Notas (Opcional)</label>
                                    <textarea
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none min-h-[100px]"
                                        placeholder="Añade detalles relevantes..."
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={!file || !title || uploading}
                                    className={`w-full py-3 rounded-xl font-semibold transition-all shadow-md
                                        ${!file || !title || uploading
                                            ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                            : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'}`}
                                >
                                    {uploading ? 'Subiendo...' : 'Guardar Documento'}
                                </button>
                            </form>
                        </div>
                    </div>

                    {/* Gallery Section */}
                    <div className="lg:col-span-2">
                        {loading ? (
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {[1, 2, 3, 4, 5, 6].map(i => (
                                    <div key={i} className="aspect-[3/4] bg-slate-200 animate-pulse rounded-2xl"></div>
                                ))}
                            </div>
                        ) : documents.length === 0 ? (
                            <div className="bg-white rounded-3xl p-12 text-center border border-slate-100">
                                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-100">
                                    <FileSearch className="w-8 h-8 text-slate-300" />
                                </div>
                                <h3 className="text-xl font-bold text-slate-800 mb-2">No hay documentos</h3>
                                <p className="text-slate-500 max-w-xs mx-auto">Tus archivos médicos aparecerán aquí una vez que los subas.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
                                {documents.map((doc) => (
                                    <div
                                        key={doc.id}
                                        onClick={() => setSelectedDoc(doc)}
                                        className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all border border-slate-100 cursor-pointer"
                                    >
                                        {/* Thumbnail Area */}
                                        <div className="aspect-[4/5] bg-slate-100 relative overflow-hidden flex items-center justify-center">
                                            {isImage(doc.file_path) ? (
                                                <img
                                                    src={getFullUrl(doc.file_path)}
                                                    alt={doc.title}
                                                    className="w-full h-full object-cover transition-transform group-hover:scale-105"
                                                />
                                            ) : (
                                                <div className="flex flex-col items-center gap-2 text-slate-400">
                                                    <FileText className="w-12 h-12" />
                                                    <span className="text-xs font-bold uppercase">PDF</span>
                                                </div>
                                            )}

                                            {/* Badge */}
                                            <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-white/90 backdrop-blur px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider text-slate-700 shadow-sm border border-white/50">
                                                {getTypeIcon(doc.document_type)}
                                                {doc.document_type}
                                            </div>

                                            {/* Hover info */}
                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                <Maximize2 className="text-white w-8 h-8" />
                                            </div>
                                        </div>

                                        {/* Info */}
                                        <div className="p-3">
                                            <h3 className="font-semibold text-slate-800 text-sm truncate">{doc.title}</h3>
                                            <p className="text-[10px] text-slate-400 mt-1">
                                                {new Date(doc.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Modal Viewer */}
            {selectedDoc && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-slate-900/90 backdrop-blur-sm"
                        onClick={() => setSelectedDoc(null)}
                    ></div>

                    <div className="relative bg-white w-full max-w-4xl max-h-[90vh] rounded-3xl overflow-hidden shadow-2xl flex flex-col">
                        {/* Modal Header */}
                        <div className="p-4 border-b flex items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-slate-50 rounded-lg">
                                    {getTypeIcon(selectedDoc.document_type)}
                                </div>
                                <div>
                                    <h3 className="font-bold text-slate-900 leading-none">{selectedDoc.title}</h3>
                                    <p className="text-xs text-slate-500 mt-1">
                                        {new Date(selectedDoc.date).toLocaleString('es-ES')}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <a
                                    href={getFullUrl(selectedDoc.file_path)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                                    title="Descargar"
                                >
                                    <Download className="w-5 h-5 text-slate-600" />
                                </a>
                                <button
                                    onClick={() => setSelectedDoc(null)}
                                    className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                                >
                                    <X className="w-6 h-6 text-slate-600" />
                                </button>
                            </div>
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-auto bg-slate-100 p-4 flex items-center justify-center">
                            {isImage(selectedDoc.file_path) ? (
                                <img
                                    src={getFullUrl(selectedDoc.file_path)}
                                    className="max-w-full h-auto rounded-lg shadow-sm"
                                    alt={selectedDoc.title}
                                />
                            ) : (
                                <div className="w-full h-full min-h-[500px] flex flex-col items-center justify-center text-slate-500 bg-white rounded-xl shadow-inner">
                                    <FileText className="w-24 h-24 mb-4 text-slate-200" />
                                    <p className="font-medium mb-4">Vista previa no disponible para este tipo de archivo</p>
                                    <a
                                        href={getFullUrl(selectedDoc.file_path)}
                                        target="_blank"
                                        className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition-all flex items-center gap-2"
                                    >
                                        <Download className="w-5 h-5" />
                                        Abrir Documento
                                    </a>
                                </div>
                            )}
                        </div>

                        {/* Modal Footer (Notes) */}
                        {selectedDoc.notes && (
                            <div className="p-6 bg-slate-50 border-t">
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Notas</h4>
                                <p className="text-slate-700 whitespace-pre-wrap">{selectedDoc.notes}</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClinicalDocs;

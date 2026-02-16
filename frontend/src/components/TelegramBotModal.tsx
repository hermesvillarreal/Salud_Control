import React, { useState } from 'react';
import { X, MessageSquare, Copy, Check, ExternalLink, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface TelegramBotModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const TelegramBotModal: React.FC<TelegramBotModalProps> = ({ isOpen, onClose }) => {
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const generateToken = async () => {
        setIsLoading(true);
        try {
            const response = await api.get('/auth/telegram-token');
            setToken(response.data.token);
        } catch (error) {
            console.error('Error generating telegram token:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCopy = () => {
        if (!token) return;
        const command = `/start ${token}`;
        navigator.clipboard.writeText(command);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
            <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                            <MessageSquare className="w-6 h-6" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Configurar Telegram</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="space-y-4">
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold shrink-0">1</div>
                            <p className="text-slate-600">Busca el bot <span className="font-semibold text-blue-600">@SaludControlBot</span> en Telegram.</p>
                        </div>
                        <div className="grid grid-cols-1 gap-2 pl-12">
                            <a
                                href="https://t.me/SaludControlBot"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center justify-center gap-2 bg-blue-50 text-blue-700 py-2 rounded-xl text-sm font-medium hover:bg-blue-100 transition-colors"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Abrir en Telegram
                            </a>
                        </div>

                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold shrink-0">2</div>
                            <p className="text-slate-600">Genera tu código de vinculación único.</p>
                        </div>

                        {!token ? (
                            <div className="pl-12">
                                <button
                                    onClick={generateToken}
                                    disabled={isLoading}
                                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-2xl font-bold transition-all shadow-lg shadow-blue-200 disabled:opacity-50"
                                >
                                    {isLoading ? <RefreshCw className="w-5 h-5 animate-spin" /> : 'Generar Código Único'}
                                </button>
                            </div>
                        ) : (
                            <div className="pl-12 space-y-4">
                                <div className="p-4 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 relative group">
                                    <p className="text-xs text-slate-400 uppercase font-bold mb-1">Tu comando de vinculación</p>
                                    <code className="text-blue-700 font-mono text-lg break-all">/start {token}</code>
                                    <button
                                        onClick={handleCopy}
                                        className="absolute right-2 top-2 p-2 bg-white rounded-lg shadow-sm border border-slate-100 hover:bg-slate-50 transition-colors text-slate-400 hover:text-blue-600"
                                        title="Copiar comando"
                                    >
                                        {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                                    </button>
                                </div>
                                <div className="flex gap-4">
                                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold shrink-0">3</div>
                                    <p className="text-slate-600 text-sm">Copia el comando de arriba y envíalo al bot en Telegram.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-6 bg-slate-50 border-t border-slate-100 text-center">
                    <p className="text-sm text-slate-500 italic">Una vez vinculado, podrás registrar peso, presión y comidas directamente por chat.</p>
                </div>
            </div>
        </div>
    );
};

export default TelegramBotModal;

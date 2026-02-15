import { Activity } from 'lucide-react'

function App() {
    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <div className="bg-white p-8 rounded-2xl shadow-xl flex flex-col items-center gap-4 max-w-md w-full border border-slate-100">
                <div className="bg-blue-100 p-4 rounded-full">
                    <Activity className="w-12 h-12 text-blue-600" />
                </div>
                <h1 className="text-3xl font-bold text-slate-900 text-center">Salud Control</h1>
                <p className="text-slate-600 text-center">
                    Monitor de Salud, Alimentación y Ejercicio.
                </p>
                <div className="w-full h-px bg-slate-100 my-2"></div>
                <div className="flex flex-col gap-2 w-full">
                    <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm font-medium text-slate-500">Estado Backend</span>
                        <span className="text-sm font-bold text-green-500">Desconectado</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default App

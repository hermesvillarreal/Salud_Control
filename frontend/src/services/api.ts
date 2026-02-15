import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor de solicitud para añadir el token JWT
api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor de respuesta para manejar errores 401
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no hemos reintentado ya
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Aquí se podría implementar la lógica de refresh token si el backend lo soporta
                // Por ahora, si falla el token, cerramos sesión y redirigimos
                useAuthStore.getState().logout();
                window.location.href = '/login';
            } catch (refreshError) {
                useAuthStore.getState().logout();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;

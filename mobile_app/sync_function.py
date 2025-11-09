def sync_with_desktop(self):
    try:
        # Obtener los datos del usuario
        records = self.db.get_user_records(1)  # Usuario por defecto
        if not records:
            QMessageBox.warning(self, 'Aviso', 'No hay datos para sincronizar')
            return

        # Preparar los datos para la sincronización
        sync_data = {
            "name": "Usuario",  # Por ahora usamos un nombre por defecto
            "email": "usuario@example.com",  # Email por defecto
            "phone": "",
            "records": records
        }

        # Intentar sincronizar con la aplicación desktop
        try:
            response = requests.post(
                'http://localhost:5000/sync_data',
                json=sync_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                QMessageBox.information(
                    self, 
                    'Éxito', 
                    'Datos sincronizados correctamente con la aplicación desktop'
                )
            else:
                QMessageBox.warning(
                    self, 
                    'Error', 
                    f'Error al sincronizar: {response.json().get("message", "Error desconocido")}'
                )

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self, 
                'Error de Conexión',
                'No se pudo conectar con la aplicación desktop. '
                'Asegúrese de que la aplicación desktop esté ejecutándose.'
            )
            
    except Exception as e:
        QMessageBox.critical(
            self, 
            'Error', 
            f'Error al preparar los datos para sincronización: {str(e)}'
        )
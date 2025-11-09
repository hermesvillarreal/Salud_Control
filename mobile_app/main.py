import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QDateEdit, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from database import MobileDatabase
import json
from datetime import datetime
import requests

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = MobileDatabase()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Salud Control - Registro de Datos')
        self.setGeometry(100, 100, 400, 600)

        # Widget y layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Fecha
        date_layout = QHBoxLayout()
        date_label = QLabel('Fecha:')
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # Peso
        weight_layout = QHBoxLayout()
        weight_label = QLabel('Peso (kg):')
        self.weight_edit = QLineEdit()
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight_edit)
        layout.addLayout(weight_layout)

        # Presión arterial
        bp_layout = QHBoxLayout()
        bp_label = QLabel('Presión Arterial:')
        self.systolic_edit = QLineEdit()
        self.systolic_edit.setPlaceholderText('Sistólica')
        self.diastolic_edit = QLineEdit()
        self.diastolic_edit.setPlaceholderText('Diastólica')
        bp_layout.addWidget(bp_label)
        bp_layout.addWidget(self.systolic_edit)
        bp_layout.addWidget(self.diastolic_edit)
        layout.addLayout(bp_layout)

        # Glucosa
        glucose_layout = QHBoxLayout()
        glucose_label = QLabel('Glucosa:')
        self.glucose_edit = QLineEdit()
        glucose_layout.addWidget(glucose_label)
        glucose_layout.addWidget(self.glucose_edit)
        layout.addLayout(glucose_layout)

        # Notas
        notes_label = QLabel('Notas:')
        layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        layout.addWidget(self.notes_edit)

        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton('Guardar')
        save_button.clicked.connect(self.save_data)
        export_button = QPushButton('Exportar')
        export_button.clicked.connect(self.export_data)
        sync_button = QPushButton('Sincronizar con Desktop')
        sync_button.clicked.connect(self.sync_with_desktop)
        button_layout.addWidget(save_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(sync_button)
        layout.addLayout(button_layout)

    def save_data(self):
        try:
            # Validar datos
            weight = float(self.weight_edit.text())
            systolic = int(self.systolic_edit.text())
            diastolic = int(self.diastolic_edit.text())
            glucose = float(self.glucose_edit.text())
            
            # Obtener fecha
            date = self.date_edit.date().toPyDate().strftime('%Y-%m-%d')
            
            # Guardar en la base de datos
            self.db.add_health_record(
                user_id=1,  # Usuario por defecto
                weight=weight,
                blood_pressure_sys=systolic,
                blood_pressure_dia=diastolic,
                glucose_level=glucose,
                notes=self.notes_edit.toPlainText()
            )
            
            QMessageBox.information(self, 'Éxito', 'Datos guardados correctamente')
            self.clear_fields()
        except ValueError as e:
            QMessageBox.warning(self, 'Error', 'Por favor, ingrese valores numéricos válidos')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar los datos: {str(e)}')

    def export_data(self):
        try:
            data = self.db.get_user_records(1)  # Usuario por defecto
            if not data:
                QMessageBox.warning(self, 'Aviso', 'No hay datos para exportar')
                return
            
            filename = f"health_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            
            QMessageBox.information(self, 'Éxito', f'Datos exportados a {filename}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al exportar los datos: {str(e)}')

    def clear_fields(self):
        self.weight_edit.clear()
        self.systolic_edit.clear()
        self.diastolic_edit.clear()
        self.glucose_edit.clear()
        self.notes_edit.clear()
        self.date_edit.setDate(QDate.currentDate())

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
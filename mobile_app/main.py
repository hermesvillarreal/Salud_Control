import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QDateEdit, QTimeEdit, QTextEdit, QMessageBox,
                           QTabWidget, QSpinBox, QDoubleSpinBox, QTableWidget,
                           QTableWidgetItem, QHeaderView, QScrollArea, QFrame,
                           QStatusBar)
from PyQt5.QtCore import Qt, QDate, QTime
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
        self.setGeometry(100, 100, 500, 700)
        
        # Estilo global para mejorar usabilidad (touch targets más grandes)
        self.setStyleSheet("""
            QSpinBox, QDoubleSpinBox { 
                min-height: 40px; 
                font-size: 14px; 
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 40px;
            }
            QPushButton {
                min-height: 40px;
                font-size: 14px;
            }
            QTableWidget {
                font-size: 12px;
            }
        """)

        # Widget y layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Crear el widget de pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Crear las pestañas
        self.tab_records = QWidget()
        self.tab_general = QWidget()
        self.tab_goals = QWidget()
        
        self.tabs.addTab(self.tab_records, "Registros Diarios")
        self.tabs.addTab(self.tab_general, "Información General")
        self.tabs.addTab(self.tab_goals, "Metas Nutricionales")

        # Barra de estado para notificaciones no intrusivas
        self.setStatusBar(QStatusBar())
        self.sync_status_label = QLabel("Estado: Sin sincronizar")
        self.statusBar().addPermanentWidget(self.sync_status_label)

        # Inicializar las pestañas
        self.init_records_tab()
        self.init_general_tab()
        self.init_goals_tab()

    def save_data(self):
        try:
            # Obtener datos directamente de los spinboxes
            weight = self.weight_edit.value()
            systolic = self.systolic_edit.value()
            diastolic = self.diastolic_edit.value()
            glucose = self.glucose_edit.value()
            
            # Verificar si hay datos en las comidas
            has_meal_data = False
            meals_summary = []
            for meal_id, meal_inputs in self.meal_inputs.items():
                meal_values = {nutrient: value.value() for nutrient, value in meal_inputs.items()}
                if any(value > 0 for value in meal_values.values()):
                    has_meal_data = True
                    if meal_id == 'breakfast':
                        meal_name = 'Desayuno'
                    elif meal_id == 'morning_snack':
                        meal_name = 'Merienda Mañana'
                    elif meal_id == 'lunch':
                        meal_name = 'Almuerzo'
                    elif meal_id == 'afternoon_snack':
                        meal_name = 'Merienda Tarde'
                    elif meal_id == 'dinner':
                        meal_name = 'Cena'
                    elif meal_id == 'post_dinner':
                        meal_name = 'Post-Cena'
                    
                    meal_summary = f"{meal_name}: P={meal_values['protein']}g, C={meal_values['carbs']}g, G={meal_values['fat']}g"
                    meals_summary.append(meal_summary)

            # Validar que haya al menos un dato (mediciones o comidas)
            if not has_meal_data and weight == 0 and systolic == 0 and diastolic == 0 and glucose == 0:
                QMessageBox.warning(self, 'Aviso', 'Por favor, ingrese al menos una medición o registro de comida')
                return
            
            # Obtener fecha y hora
            date = self.date_edit.date().toPyDate()
            time = self.time_edit.time().toPyTime()
            datetime_str = datetime.combine(date, time).strftime('%Y-%m-%d %H:%M:%S')
            
            # Preparar datos de comidas
            meals_data = {}
            for meal_id in self.meal_inputs:
                meals_data[meal_id] = {
                    'protein': self.meal_inputs[meal_id]['protein'].value(),
                    'carbs': self.meal_inputs[meal_id]['carbs'].value(),
                    'fat': self.meal_inputs[meal_id]['fat'].value()
                }

            # Guardar en la base de datos
            self.db.add_health_record(
                user_id=1,  # Usuario por defecto
                weight=weight,
                blood_pressure_sys=systolic,
                blood_pressure_dia=diastolic,
                glucose_level=glucose,
                notes=self.notes_edit.toPlainText(),
                datetime_str=datetime_str,
                meals_data=meals_data
            )
            
            # Mostrar resumen de los datos guardados
            resumen = f"Datos guardados:\nFecha y hora: {datetime_str}\n"
            
            # Agregar mediciones si existen
            if weight > 0:
                resumen += f"Peso: {weight} kg\n"
            if systolic > 0 or diastolic > 0:
                resumen += f"Presión Arterial: {systolic}/{diastolic} mmHg\n"
            if glucose > 0:
                resumen += f"Glucosa: {glucose} mg/dL\n"
            
            # Agregar resumen de comidas si hay datos
            if meals_summary:
                resumen += "\nRegistro de comidas:\n"
                resumen += "\n".join(meals_summary)
            
            # Feedback no intrusivo
            self.statusBar().showMessage("Datos guardados correctamente", 3000)
            
            # Recargar el último registro y mantener los valores en los campos
            self.load_last_record()
            
            # Actualizar el progreso en la pestaña de metas
            self.update_progress_display()
            
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

    def init_records_tab(self):
        # Layout principal para la pestaña
        main_layout = QVBoxLayout()
        self.tab_records.setLayout(main_layout)

        # Crear área de desplazamiento
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        # Contenedor para todos los widgets
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        # Fecha y Hora
        datetime_layout = QHBoxLayout()
        date_label = QLabel('Fecha:')
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        time_label = QLabel('Hora:')
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        datetime_layout.addWidget(date_label)
        datetime_layout.addWidget(self.date_edit)
        datetime_layout.addWidget(time_label)
        datetime_layout.addWidget(self.time_edit)
        scroll_layout.addLayout(datetime_layout)

        # Último registro (vista de solo lectura)
        last_record_frame = QFrame()
        last_record_frame.setFrameStyle(QFrame.StyledPanel)
        last_record_frame.setStyleSheet('QFrame { background-color: #e6f3ff; border-radius: 5px; margin: 2px; padding: 10px; }')
        last_record_layout = QVBoxLayout(last_record_frame)
        
        self.last_values_label = QLabel()
        self.last_values_label.setStyleSheet('padding: 5px;')
        last_record_layout.addWidget(self.last_values_label)
        
        scroll_layout.addWidget(last_record_frame)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(separator)

        # Nueva medición
        new_record_label = QLabel('Nueva Medición:')
        new_record_label.setStyleSheet('font-weight: bold; font-size: 11pt; margin-top: 10px;')
        scroll_layout.addWidget(new_record_label)

        # Peso
        weight_layout = QHBoxLayout()
        weight_label = QLabel('Peso (kg):')
        self.weight_edit = QDoubleSpinBox()
        self.weight_edit.setRange(0, 300)
        self.weight_edit.setDecimals(1)
        self.weight_edit.setSingleStep(0.1)
        self.weight_edit.setSuffix(' kg')
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight_edit)
        scroll_layout.addLayout(weight_layout)

        # Presión arterial
        bp_layout = QHBoxLayout()
        bp_label = QLabel('Presión Arterial:')
        self.systolic_edit = QSpinBox()
        self.systolic_edit.setRange(0, 300)
        self.systolic_edit.setSuffix(' mmHg')
        self.diastolic_edit = QSpinBox()
        self.diastolic_edit.setRange(0, 200)
        self.diastolic_edit.setSuffix(' mmHg')
        bp_layout.addWidget(bp_label)
        bp_layout.addWidget(self.systolic_edit)
        bp_layout.addWidget(self.diastolic_edit)
        scroll_layout.addLayout(bp_layout)

        # Glucosa
        glucose_layout = QHBoxLayout()
        glucose_label = QLabel('Glucosa:')
        self.glucose_edit = QDoubleSpinBox()
        self.glucose_edit.setRange(0, 500)
        self.glucose_edit.setDecimals(1)
        self.glucose_edit.setSingleStep(1.0)
        self.glucose_edit.setSuffix(' mg/dL')
        glucose_layout.addWidget(glucose_label)
        glucose_layout.addWidget(self.glucose_edit)
        scroll_layout.addLayout(glucose_layout)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(separator)

        # Registros de comidas
        meals_label = QLabel('Registro de Comidas:')
        meals_label.setStyleSheet('font-weight: bold; font-size: 12pt; margin-top: 10px; margin-bottom: 10px;')
        scroll_layout.addWidget(meals_label)

        # Encabezados de nutrientes
        nutrients_header = QHBoxLayout()
        header_spacer = QLabel('')  # Espacio para alinear con el nombre de la comida
        nutrients_header.addWidget(header_spacer)
        for nutrient, label in [('Proteínas (P)', ''), ('Carbohidratos (C)', ''), ('Grasas (G)', '')]:
            nutrient_label = QLabel(nutrient)
            nutrient_label.setStyleSheet('font-weight: bold;')
            nutrient_label.setAlignment(Qt.AlignCenter)
            nutrients_header.addWidget(nutrient_label)
        scroll_layout.addLayout(nutrients_header)

        # Diccionario para almacenar los campos de entrada
        self.meal_inputs = {}
        
        # Lista de comidas y sus etiquetas
        meals = [
            ('breakfast', 'Desayuno'),
            ('morning_snack', 'Merienda Mañana'),
            ('lunch', 'Almuerzo'),
            ('afternoon_snack', 'Merienda Tarde'),
            ('dinner', 'Cena'),
            ('post_dinner', 'Post-Cena')
        ]

        # Crear campos para cada comida
        for meal_id, meal_name in meals:
            # Crear y configurar el frame para la comida
            meal_frame = QFrame()
            meal_frame.setFrameStyle(QFrame.StyledPanel)
            meal_frame.setStyleSheet('QFrame { background-color: #f0f0f0; border-radius: 5px; margin: 2px; }')
            
            # Crear el layout dentro del frame
            meal_layout = QHBoxLayout()
            meal_frame.setLayout(meal_layout)
            
            # Agregar etiqueta de la comida
            meal_label = QLabel(meal_name + ':')
            meal_label.setMinimumWidth(120)
            meal_label.setStyleSheet('font-weight: bold;')
            meal_layout.addWidget(meal_label)

            self.meal_inputs[meal_id] = {}
            
            # Campos para proteínas, carbohidratos y grasas
            for nutrient, label in [('protein', 'P'), ('carbs', 'C'), ('fat', 'G')]:
                nutrient_edit = QDoubleSpinBox()
                nutrient_edit.setRange(0, 1000)
                nutrient_edit.setDecimals(1)
                nutrient_edit.setSuffix('g')
                nutrient_edit.setMinimumWidth(80)
                nutrient_edit.setStyleSheet('background-color: white;')
                
                self.meal_inputs[meal_id][nutrient] = nutrient_edit
                meal_layout.addWidget(nutrient_edit)

            meal_layout.addStretch()  # Espacio flexible al final
            scroll_layout.addWidget(meal_frame)

        # Notas
        notes_label = QLabel('Notas:')
        scroll_layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        scroll_layout.addWidget(self.notes_edit)

        # Agregar espacio en blanco al final del área de desplazamiento
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        scroll_layout.addWidget(spacer)

        # Botones (fuera del área de desplazamiento)
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
        main_layout.addLayout(button_layout)

        # Una vez que todos los widgets están creados, cargar el último registro
        self.load_last_record()

        # Configurar orden de tabulación (Tab Order)
        self.setTabOrder(self.date_edit, self.time_edit)
        self.setTabOrder(self.time_edit, self.weight_edit)
        self.setTabOrder(self.weight_edit, self.systolic_edit)
        self.setTabOrder(self.systolic_edit, self.diastolic_edit)
        self.setTabOrder(self.diastolic_edit, self.glucose_edit)

    def init_general_tab(self):
        layout = QVBoxLayout()
        self.tab_general.setLayout(layout)

        # Edad
        age_layout = QHBoxLayout()
        age_label = QLabel('Edad:')
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        age_layout.addWidget(age_label)
        age_layout.addWidget(self.age_spin)
        layout.addLayout(age_layout)

        # Altura
        height_layout = QHBoxLayout()
        height_label = QLabel('Altura (cm):')
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0, 250)
        self.height_spin.setDecimals(1)
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)

        # Peso Inicial
        init_weight_layout = QHBoxLayout()
        init_weight_label = QLabel('Peso Inicial (kg):')
        self.init_weight_spin = QDoubleSpinBox()
        self.init_weight_spin.setRange(0, 300)
        self.init_weight_spin.setDecimals(1)
        init_weight_layout.addWidget(init_weight_label)
        init_weight_layout.addWidget(self.init_weight_spin)
        layout.addLayout(init_weight_layout)

        # Condición Médica
        medical_condition_label = QLabel('Condición Médica:')
        layout.addWidget(medical_condition_label)
        self.medical_condition_edit = QTextEdit()
        self.medical_condition_edit.setMaximumHeight(100)
        layout.addWidget(self.medical_condition_edit)

        # Medicación
        medication_label = QLabel('Medicación:')
        layout.addWidget(medication_label)
        self.medication_edit = QTextEdit()
        self.medication_edit.setMaximumHeight(100)
        layout.addWidget(self.medication_edit)

        # Objetivo Principal
        objective_label = QLabel('Objetivo Principal:')
        layout.addWidget(objective_label)
        self.objective_edit = QTextEdit()
        self.objective_edit.setMaximumHeight(100)
        layout.addWidget(self.objective_edit)

        # Botón de guardar información general
        save_general_button = QPushButton('Guardar Información General')
        save_general_button.clicked.connect(self.save_general_info)
        layout.addWidget(save_general_button)

        # Cargar datos existentes
        self.load_general_info()

    def save_general_info(self):
        try:
            self.db.save_general_info(
                user_id=1,  # Usuario por defecto
                age=self.age_spin.value(),
                height=self.height_spin.value(),
                initial_weight=self.init_weight_spin.value(),
                medical_condition=self.medical_condition_edit.toPlainText(),
                medication=self.medication_edit.toPlainText(),
                main_objective=self.objective_edit.toPlainText()
            )
            QMessageBox.information(self, 'Éxito', 'Información general guardada correctamente')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar la información general: {str(e)}')

    def load_general_info(self):
        try:
            info = self.db.get_general_info(1)  # Usuario por defecto
            if info:
                self.age_spin.setValue(info['age'] if info['age'] is not None else 0)
                self.height_spin.setValue(info['height'] if info['height'] is not None else 0)
                self.init_weight_spin.setValue(info['initial_weight'] if info['initial_weight'] is not None else 0)
                self.medical_condition_edit.setPlainText(info['medical_condition'] or '')
                self.medication_edit.setPlainText(info['medication'] or '')
                self.objective_edit.setPlainText(info['main_objective'] or '')
        except Exception as e:
            QMessageBox.warning(self, 'Advertencia', f'Error al cargar la información general: {str(e)}')

    def init_goals_tab(self):
        layout = QVBoxLayout()
        self.tab_goals.setLayout(layout)

        # Crear la tabla de metas nutricionales
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(4)
        self.goals_table.setHorizontalHeaderLabels(['OBJETIVO', 'UNIDAD', 'CANTIDAD', 'NOTA CLAVE'])
        
        # Configurar el comportamiento de la tabla
        self.goals_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.goals_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.goals_table.setEditTriggers(QTableWidget.DoubleClicked)
        
        layout.addWidget(self.goals_table)

        # Botón para guardar cambios
        save_goals_button = QPushButton('Guardar Metas')
        save_goals_button.clicked.connect(self.save_goals)
        layout.addWidget(save_goals_button)

        # Agregar un frame para el progreso diario
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel)
        progress_frame.setStyleSheet('QFrame { background-color: #f0f0f0; border-radius: 5px; margin: 5px; padding: 10px; }')
        progress_layout = QVBoxLayout(progress_frame)

        # Label para mostrar el progreso
        self.progress_label = QLabel()
        self.progress_label.setTextFormat(Qt.RichText)
        self.progress_label.setStyleSheet('font-size: 11pt;')
        progress_layout.addWidget(self.progress_label)

        # Botón para actualizar el progreso
        update_progress_button = QPushButton('Actualizar Progreso')
        update_progress_button.clicked.connect(self.update_progress_display)
        progress_layout.addWidget(update_progress_button)

        layout.addWidget(progress_frame)

        # Cargar datos predeterminados si no hay datos existentes
        self.load_goals()
        # Mostrar el progreso inicial
        self.update_progress_display()

    def calculate_todays_totals(self):
        try:
            # Obtener el último registro del día
            last_record = self.db.get_last_record(1)  # Usuario por defecto
            
            if not last_record:
                print("No se encontraron registros")
                return {'protein': 0, 'carbs': 0, 'fat': 0}

            # Verificar si el último registro es de hoy
            today = QDate.currentDate().toString('yyyy-MM-dd')
            record_date = last_record['datetime'].split(' ')[0]
            
            print(f"Fecha del último registro: {record_date}, Comparando con hoy: {today}")
            
            if record_date != today:
                print("El último registro no es de hoy")
                return {'protein': 0, 'carbs': 0, 'fat': 0}
            
            print("Procesando último registro:", last_record)
            
            daily_totals = {
                'protein': 0,
                'carbs': 0,
                'fat': 0
            }
            
            # Procesar las comidas del último registro
            meals = last_record.get('meals', {})
            if not meals:
                print("No hay datos de comidas en el último registro")
                return daily_totals
                
            print("Datos de comidas encontrados:", meals)
            
            # Sumar los nutrientes de cada comida
            for meal_name, meal_data in meals.items():
                if not isinstance(meal_data, dict):
                    print(f"Datos inválidos para {meal_name}")
                    continue
                    
                protein = meal_data.get('protein', 0) or 0
                carbs = meal_data.get('carbs', 0) or 0
                fat = meal_data.get('fat', 0) or 0
                
                daily_totals['protein'] += protein
                daily_totals['carbs'] += carbs
                daily_totals['fat'] += fat
                
                print(f"Comida {meal_name}: P={protein}g, C={carbs}g, G={fat}g")
            
            print("\nTotales del día:", daily_totals)
            return daily_totals
        except Exception as e:
            print(f"Error calculando totales diarios: {str(e)}")
            return None

    def update_progress_display(self):
        daily_totals = self.calculate_todays_totals()
        if not daily_totals:
            self.progress_label.setText("Error al calcular los totales diarios")
            return

        goals = self.db.get_nutrition_goals(1)
        if not goals:
            self.progress_label.setText("No hay metas nutricionales definidas")
            return

        progress_text = "<h3>Progreso del día:</h3>"
        
        for goal in goals:
            if goal['objective'].lower().startswith('proteína'):
                target = goal['quantity']
                current = daily_totals['protein']
                status = "✅" if current >= target else "❌"
                progress = (current / target * 100) if target > 0 else 0
                progress_text += f"<p><b>Proteínas:</b> {current:.1f}g / {target}g ({progress:.1f}%) {status}</p>"
                
            elif goal['objective'].lower().startswith('carbohidrato'):
                target = goal['quantity']
                current = daily_totals['carbs']
                status = "✅" if current <= target else "❌"
                progress = (current / target * 100) if target > 0 else 0
                progress_text += f"<p><b>Carbohidratos:</b> {current:.1f}g / {target}g ({progress:.1f}%) {status}</p>"
                
            elif goal['objective'].lower().startswith('grasa'):
                target = goal['quantity']
                current = daily_totals['fat']
                status = "✅" if current <= target else "❌"
                progress = (current / target * 100) if target > 0 else 0
                progress_text += f"<p><b>Grasas:</b> {current:.1f}g / {target}g ({progress:.1f}%) {status}</p>"

        self.progress_label.setText(progress_text)

    def load_goals(self):
        try:
            goals = self.db.get_nutrition_goals(1)  # Usuario por defecto
            
            # Si no hay metas guardadas, cargar valores predeterminados
            if not goals:
                default_goals = [
                    {
                        'objective': 'Calorías (Tasa de Déficit)',
                        'unit': 'kcal',
                        'quantity': 2000,
                        'key_note': 'Meta para pérdida de grasa.'
                    },
                    {
                        'objective': 'Proteínas',
                        'unit': 'gramos',
                        'quantity': 192,
                        'key_note': 'Clave para preservar músculo.'
                    },
                    {
                        'objective': 'Carbohidratos Netos',
                        'unit': 'gramos',
                        'quantity': 135,
                        'key_note': 'Máximo para control de prediabetes (HbA1c).'
                    },
                    {
                        'objective': 'Grasas',
                        'unit': 'gramos',
                        'quantity': 77,
                        'key_note': 'Controladas para déficit calórico.'
                    }
                ]
                
                # Guardar metas predeterminadas en la base de datos
                for goal in default_goals:
                    self.db.save_nutrition_goal(
                        user_id=1,
                        objective=goal['objective'],
                        unit=goal['unit'],
                        quantity=goal['quantity'],
                        key_note=goal['key_note']
                    )
                goals = default_goals

            # Configurar la tabla con las metas
            self.goals_table.setRowCount(len(goals))
            for i, goal in enumerate(goals):
                self.goals_table.setItem(i, 0, QTableWidgetItem(goal['objective']))
                self.goals_table.setItem(i, 1, QTableWidgetItem(goal['unit']))
                self.goals_table.setItem(i, 2, QTableWidgetItem(str(goal['quantity'])))
                self.goals_table.setItem(i, 3, QTableWidgetItem(goal['key_note']))

        except Exception as e:
            QMessageBox.warning(self, 'Advertencia', f'Error al cargar las metas: {str(e)}')

    def save_goals(self):
        try:
            for row in range(self.goals_table.rowCount()):
                objective = self.goals_table.item(row, 0).text()
                unit = self.goals_table.item(row, 1).text()
                quantity = float(self.goals_table.item(row, 2).text())
                key_note = self.goals_table.item(row, 3).text()

                self.db.save_nutrition_goal(
                    user_id=1,
                    objective=objective,
                    unit=unit,
                    quantity=quantity,
                    key_note=key_note
                )

            QMessageBox.information(self, 'Éxito', 'Metas nutricionales guardadas correctamente')
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Por favor, ingrese valores numéricos válidos para las cantidades')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar las metas: {str(e)}')

    def load_last_record(self):
        try:
            last_record = self.db.get_last_record(1)  # Usuario por defecto
            if last_record:
                # Mostrar solo la fecha del último registro
                last_values_text = f"<p><b>Última Medición:</b> {last_record['datetime']}</p>"
                self.last_values_label.setText(last_values_text)
                
                # Verificar si el registro es de hoy
                today = QDate.currentDate().toString('yyyy-MM-dd')
                record_date = last_record['datetime'].split(' ')[0]
                
                # Siempre mantener el último peso registrado
                if last_record['weight']:
                    self.weight_edit.setValue(last_record['weight'])
                
                # Si el registro es de hoy, cargar todos los valores
                if record_date == today:
                    if last_record['blood_pressure_sys'] or last_record['blood_pressure_dia']:
                        self.systolic_edit.setValue(last_record['blood_pressure_sys'] if last_record['blood_pressure_sys'] else 0)
                        self.diastolic_edit.setValue(last_record['blood_pressure_dia'] if last_record['blood_pressure_dia'] else 0)
                    if last_record['glucose_level']:
                        self.glucose_edit.setValue(last_record['glucose_level'])

                    # Actualizar los campos de comidas
                    for meal_id, meal_data in last_record['meals'].items():
                        if any(value > 0 for value in meal_data.values()):
                            for nutrient, value in meal_data.items():
                                if value is not None and value > 0:
                                    self.meal_inputs[meal_id][nutrient].setValue(value)
                else:
                    # Si no es de hoy, limpiar todos los campos excepto el peso
                    self.systolic_edit.setValue(0)
                    self.diastolic_edit.setValue(0)
                    self.glucose_edit.setValue(0)
                    
                    # Limpiar todos los campos de comidas
                    for meal_inputs in self.meal_inputs.values():
                        for spinbox in meal_inputs.values():
                            spinbox.setValue(0)
                    
                    # Limpiar notas
                    self.notes_edit.clear()

                # Mantener la fecha y hora actuales para el nuevo registro
                self.date_edit.setDate(QDate.currentDate())
                self.time_edit.setTime(QTime.currentTime())
            else:
                self.last_values_label.setText("No hay registros previos")
        except Exception as e:
            self.last_values_label.setText("Error al cargar el último registro")
            print(f"Error al cargar el último registro: {str(e)}")

    def clear_fields(self):
        self.weight_edit.setValue(0)
        self.systolic_edit.setValue(0)
        self.diastolic_edit.setValue(0)
        self.glucose_edit.setValue(0)
        self.notes_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        
        # Limpiar campos de comidas
        for meal in self.meal_inputs.values():
            for spinbox in meal.values():
                spinbox.setValue(0)

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
                    self.sync_status_label.setText("Estado: Sincronizado ✅")
                    self.statusBar().showMessage("Sincronización completada", 3000)
                else:
                    QMessageBox.warning(
                        self, 
                        'Error', 
                        f'Error al sincronizar: {response.json().get("message", "Error desconocido")}'
                    )

            except requests.exceptions.ConnectionError:
                self.sync_status_label.setText("Estado: Error de conexión ❌")
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
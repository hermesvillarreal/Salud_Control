import pandas as pd
import numpy as np
from database import MobileDatabase
import json
import pywhatkit
from datetime import datetime

class HealthApp:
    def __init__(self):
        self.db = MobileDatabase()

    def register_user(self, name, email, phone):
        return self.db.add_user(name, email, phone)

    def add_health_record(self, user_id, weight, blood_pressure_sys, 
                         blood_pressure_dia, glucose_level, notes=""):
        self.db.add_health_record(
            user_id, weight, blood_pressure_sys, 
            blood_pressure_dia, glucose_level, notes
        )

    def get_user_summary(self, user_id):
        records = self.db.get_user_records(user_id)
        if not records:
            return "No records found"

        df = pd.DataFrame(records, columns=[
            'id', 'user_id', 'date', 'weight', 'blood_pressure_sys',
            'blood_pressure_dia', 'glucose_level', 'notes'
        ])

        summary = {
            'latest_weight': df['weight'].iloc[0],
            'avg_blood_pressure': f"{df['blood_pressure_sys'].mean():.0f}/{df['blood_pressure_dia'].mean():.0f}",
            'avg_glucose': df['glucose_level'].mean(),
            'total_records': len(df)
        }

        return summary

    def export_data(self, user_id):
        data = self.db.export_to_json(user_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"health_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            f.write(data)
            
        return filename

    def send_report_via_whatsapp(self, phone_number, user_id):
        summary = self.get_user_summary(user_id)
        message = f"""Health Report Summary:
        Latest Weight: {summary['latest_weight']} kg
        Average Blood Pressure: {summary['avg_blood_pressure']}
        Average Glucose: {summary['avg_glucose']} mg/dL
        Total Records: {summary['total_records']}
        """
        
        # Export data to file
        filename = self.export_data(user_id)
        
        # Send message and file via WhatsApp
        try:
            # Send message
            pywhatkit.sendwhatmsg_instantly(
                phone_number,
                message,
                wait_time=10
            )
            
            # Note: You would need additional configuration to send files via WhatsApp
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")
            return False
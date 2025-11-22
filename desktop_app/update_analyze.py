#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update analyze_health_data function to query separate tables
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# analyze_health_data function replacement
new_analyze = '''@app.route("/analyze")
@login_required
def analyze_health_data():
    user_id = current_user.id
    try:
        # Query separate tables
        weight_query = text("SELECT date, weight FROM weight_records WHERE user_id = :user_id ORDER BY date")
        bp_query = text("SELECT date, systolic as blood_pressure_sys, diastolic as blood_pressure_dia FROM blood_pressure_records WHERE user_id = :user_id ORDER BY date")
        glucose_query = text("SELECT date, glucose_level FROM glucose_records WHERE user_id = :user_id ORDER BY date")
        
        with engine.connect() as conn:
            weight_df = pd.read_sql_query(weight_query, conn, params={"user_id": user_id})
            bp_df = pd.read_sql_query(bp_query, conn, params={"user_id": user_id})
            glucose_df = pd.read_sql_query(glucose_query, conn, params={"user_id": user_id})
        
        # Merge data on date (outer join to keep all dates)
        data = weight_df.merge(bp_df, on='date', how='outer')
        data = data.merge(glucose_df, on='date', how='outer')
        
        if data.empty:
            return jsonify({"error": "No records found"}), 404
            
        # Realizar análisis básico
        analysis_result = basic_analysis(data)
        
        # Si la API de OpenAI está disponible, agregar análisis de IA
        if openai_api_key:
            try:
                analysis_prompt = f"""
                Analyze the following health metrics:
                Weight: Mean {analysis_result['statistics']['weight']['mean']:.1f}kg, 
                       Trend: {analysis_result['statistics']['weight']['trend']}
                Blood Pressure: Mean {analysis_result['statistics']['blood_pressure']['sys_mean']:.0f}/
                              {analysis_result['statistics']['blood_pressure']['dia_mean']:.0f}
                Glucose: Mean {analysis_result['statistics']['glucose']['mean']:.1f}, 
                        Standard Deviation {analysis_result['statistics']['glucose']['std']:.1f}
                
                Provide a brief health analysis and recommendations.
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a health analysis assistant."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                )
                analysis_result['ai_analysis'] = response.choices[0].message.content
            except Exception as e:
                analysis_result['ai_analysis'] = f"AI analysis unavailable: {str(e)}"
        
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

# Find and replace analyze_health_data function
pattern = r'@app\.route\("/analyze"\).*?(?=\n    # Calculate basic statistics|\nimport os\nfrom dotenv import load_dotenv|\n@app\.route|def send_report|\Z)'
content = re.sub(pattern, new_analyze + '\n\n', content, flags=re.DOTALL)

print("✓ Updated analyze_health_data function")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ app.py updated successfully!")
print("  - analyze_health_data() now queries separate tables and merges them")

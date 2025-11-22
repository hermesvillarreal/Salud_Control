#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update get_health_data function to query separate tables
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# get_health_data function replacement - use raw string to avoid escaping issues
new_get_health_data = r"""@app.route('/health_data', methods=['GET'])
@login_required
def get_health_data():
    try:
        # Query all separate tables using UNION ALL
        combined_query = text("""+"''"\
            SELECT w.date, w.weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia, \
                   NULL as glucose_level, NULL as meals\
            FROM weight_records w\
            WHERE w.user_id = :user_id\
            UNION ALL\
            SELECT b.date, NULL as weight, b.systolic as blood_pressure_sys, b.diastolic as blood_pressure_dia,\
                   NULL as glucose_level, NULL as meals\
            FROM blood_pressure_records b\
            WHERE b.user_id = :user_id\
            UNION ALL\
            SELECT g.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,\
                   g.glucose_level, NULL as meals\
            FROM glucose_records g\
            WHERE g.user_id = :user_id\
            UNION ALL\
            SELECT f.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,\
                   NULL as glucose_level, f.meals\
            FROM food_records f\
            WHERE f.user_id = :user_id\
            ORDER BY date\
        """+r""")
        
        with engine.connect() as conn:
            df = pd.read_sql_query(combined_query, conn, params={"user_id": current_user.id})
        
        # Replace NaN with None for JSON serialization
        df = df.where(pd.notnull(df), None)
        
        return jsonify({
            'status': 'success',
            'user': {
                'name': current_user.name,
                'email': current_user.email,
                'phone': current_user.phone
            },
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500"""

# Find and replace get_health_data function
pattern = r'@app\.route\(\'/health_data\', methods=\[\'GET\'\]\).*?(?=\n@app\.route|if __name__|$)'
match = re.search(pattern, content, flags=re.DOTALL)

if match:
    content = content[:match.start()] + new_get_health_data + '\n\n' + content[match.end():]
    print("✓ Updated get_health_data function")
else:
    print("✗ Could not find get_health_data function to replace")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ app.py updated successfully!")
print("  - get_health_data() now queries separate tables using UNION ALL")

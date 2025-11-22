#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update only the query part of get_health_data function
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Old query to replace (lines 560-566)
old_query = """        query = text('''
            SELECT u.name, u.email, u.phone, h.date, h.weight, 
                   h.blood_pressure_sys, h.blood_pressure_dia, h.glucose_level, h.meals
            FROM users u
            JOIN health_records h ON u.id = h.user_id
            WHERE u.id = :user_id
        ''')
        with engine.connect() as conn:
            data = pd.read_sql_query(query, conn, params={"user_id": current_user.id})
        
        # Convert to DataFrame
        # columns are inferred by read_sql_query
        df = data"""

# New query using UNION ALL
new_query = """        # Query all separate tables using UNION ALL
        combined_query = text(\"\"\"
            SELECT w.date, w.weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia, 
                   NULL as glucose_level, NULL as meals
            FROM weight_records w
            WHERE w.user_id = :user_id
            UNION ALL
            SELECT b.date, NULL as weight, b.systolic as blood_pressure_sys, b.diastolic as blood_pressure_dia,
                   NULL as glucose_level, NULL as meals
            FROM blood_pressure_records b
            WHERE b.user_id = :user_id
            UNION ALL
            SELECT g.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,
                   g.glucose_level, NULL as meals
            FROM glucose_records g
            WHERE g.user_id = :user_id
            UNION ALL
            SELECT f.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,
                   NULL as glucose_level, f.meals
            FROM food_records f
            WHERE f.user_id = :user_id
            ORDER BY date
        \"\"\")
        
        with engine.connect() as conn:
            df = pd.read_sql_query(combined_query, conn, params={"user_id": current_user.id})
        
        # Replace NaN with None for JSON serialization
        df = df.where(pd.notnull(df), None)
        
        # Add user info to the response
        df.insert(0, 'name', current_user.name)
        df.insert(1, 'email', current_user.email)
        df.insert(2, 'phone', current_user.phone)"""

# Replace the query section
if old_query in content:
    content = content.replace(old_query, new_query)
    print("✓ Updated get_health_data query")
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ app.py updated successfully!")
    print("  - get_health_data() now queries separate tables using UNION ALL")
else:
    print("✗ Could not find the exact query to replace")
    print("  This might mean the function was already updated or has different formatting")

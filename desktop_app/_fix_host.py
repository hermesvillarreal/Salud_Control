#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Read the file
with open('desktop_app/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the app.run line
content = content.replace(
    'app.run(debug=True)',
    "app.run(host='0.0.0.0', port=5000, debug=True)"
)

# Write back
with open('desktop_app/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Fixed app.run() to listen on all interfaces (0.0.0.0:5000)')

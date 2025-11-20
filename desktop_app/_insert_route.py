#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Read the original file
with open('desktop_app/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Read the route to insert
with open('desktop_app/_add_record_route.txt', 'r', encoding='utf-8') as f:
    route = f.read()

# Insert after line 133 (index 133)
new_lines = lines[:133] + [route + '\n'] + lines[133:]

# Write back
with open('desktop_app/app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✓ add_record route added successfully')

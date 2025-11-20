#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script to change weight chart from line to bar

with open('desktop_app/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace px.line with px.bar for weight chart
content = content.replace(
    "fig_weight = px.line(daily_weight, x='date_only', y='weight', title='Weight Over Time')",
    "fig_weight = px.bar(daily_weight, x='date_only', y='weight', title='Weight Over Time')"
)

# Remove the line update_traces for markers (not needed for bars)
content = content.replace(
    "fig_weight.update_traces(mode='lines+markers', marker=dict(size=8))",
    "fig_weight.update_traces(marker=dict(color='#4CAF50', line=dict(color='#2E7D32', width=2)))"
)

# Write back
with open('desktop_app/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Successfully changed weight chart to bar chart')

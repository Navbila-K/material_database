#!/usr/bin/env python3
"""FAST CHART VERIFICATION - All 6 Chart Types"""
import sys, os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from db.database import DatabaseManager
from db.query import MaterialQuerier

def fetch_data(querier, material):
    mat_data = querier.get_material_by_name(material, apply_overrides=False)
    if not mat_data: return {}
    
    property_dict = {}
    for cat_name, cat_data in mat_data.get('properties', {}).items():
        if not isinstance(cat_data, dict): continue
        for prop_name, prop_data in cat_data.items():
            if not isinstance(prop_data, dict): continue
            unit = prop_data.get('unit', '')
            normalized = prop_name.lower().replace(' ', '_')
            if normalized not in property_dict: property_dict[normalized] = []
            for entry in prop_data.get('entries', []):
                if entry.get('value') and entry.get('value').lower() != 'null':
                    try:
                        property_dict[normalized].append({'value': float(entry['value']), 'unit': unit, 'ref': entry.get('ref', '')})
                    except: pass
    return property_dict

output_dir = Path(__file__).parent / "chart_verification_output"
output_dir.mkdir(exist_ok=True)

db = DatabaseManager()
q = MaterialQuerier(db)
mats_data = {m: fetch_data(q, m) for m in ["Copper", "Aluminum"]}
props = ["density", "cp"]
colors = ['#e74c3c', '#3498db']

results = {}

# Line Chart
fig, ax = plt.subplots(figsize=(10,6))
count = 0
for i, (mat, data) in enumerate(mats_data.items()):
    for prop in props:
        if prop in data and data[prop]:
            vals = [v['value'] for v in data[prop]]
            ax.plot(range(len(vals)), vals, 'o-', label=f"{mat}-{prop}", color=colors[i], lw=2, ms=6)
            count += 1
if count: ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("Line Chart"); plt.savefig(output_dir/"line.png", dpi=150); results['Line']='PASS'
else: results['Line']='FAIL'
plt.close()

# Bar Chart  
fig, ax = plt.subplots(figsize=(10,6))
bar_data = {m: {p: np.mean([v['value'] for v in data[p]]) for p in props if p in data and data[p]} for m, data in mats_data.items()}
x = np.arange(len(props))
width = 0.35
for i, (mat, pdata) in enumerate(bar_data.items()):
    vals = [pdata.get(p, 0) for p in props]
    ax.bar(x + i*width, vals, width, label=mat, color=colors[i])
ax.set_xticks(x + width/2); ax.set_xticklabels(props); ax.legend(); ax.grid(True, alpha=0.3, axis='y'); ax.set_title("Bar Chart"); plt.savefig(output_dir/"bar.png", dpi=150); results['Bar']='PASS'
plt.close()

# Scatter
fig, ax = plt.subplots(figsize=(10,6))
count = 0
for i, (mat, data) in enumerate(mats_data.items()):
    for prop in props:
        if prop in data and data[prop]:
            vals = [v['value'] for v in data[prop]]
            ax.scatter(range(len(vals)), vals, s=100, label=f"{mat}-{prop}", color=colors[i], alpha=0.7, edgecolors='white', lw=2)
            count += 1
if count: ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("Scatter Chart"); plt.savefig(output_dir/"scatter.png", dpi=150); results['Scatter']='PASS'
else: results['Scatter']='FAIL'
plt.close()

# Area
fig, ax = plt.subplots(figsize=(10,6))
count = 0
for i, (mat, data) in enumerate(mats_data.items()):
    for prop in props:
        if prop in data and data[prop]:
            vals = [v['value'] for v in data[prop]]
            ax.fill_between(range(len(vals)), vals, alpha=0.4, color=colors[i], label=f"{mat}-{prop}")
            ax.plot(range(len(vals)), vals, color=colors[i], lw=2)
            count += 1
if count: ax.legend(); ax.grid(True, alpha=0.3); ax.set_title("Area Chart"); plt.savefig(output_dir/"area.png", dpi=150); results['Area']='PASS'
else: results['Area']='FAIL'
plt.close()

# Pie
fig, ax = plt.subplots(figsize=(8,8))
mat = list(mats_data.keys())[0]
data = mats_data[mat]
labels, sizes = [], []
for prop in props:
    if prop in data and data[prop]:
        labels.append(prop)
        sizes.append(np.mean([v['value'] for v in data[prop]]))
if sizes: ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors); ax.set_title(f"Pie Chart - {mat}"); plt.savefig(output_dir/"pie.png", dpi=150); results['Pie']='PASS'
else: results['Pie']='FAIL'
plt.close()

# Histogram
fig, ax = plt.subplots(figsize=(10,6))
count = 0
for i, (mat, data) in enumerate(mats_data.items()):
    for prop in props:
        if prop in data and data[prop]:
            vals = [v['value'] for v in data[prop]]
            ax.hist(vals, bins=min(10,len(vals)), alpha=0.6, color=colors[i], label=f"{mat}-{prop}", edgecolor='white')
            count += 1
if count: ax.legend(); ax.grid(True, alpha=0.3, axis='y'); ax.set_title("Histogram"); plt.savefig(output_dir/"histogram.png", dpi=150); results['Histogram']='PASS'
else: results['Histogram']='FAIL'
plt.close()

print("\n"+"="*60)
print("CHART VERIFICATION RESULTS")
print("="*60)
for chart, result in results.items():
    status = "✓" if result=="PASS" else "✗"
    print(f"{status} {chart:12} : {result}")
passed = sum(1 for r in results.values() if r=="PASS")
print(f"\n{passed}/6 TESTS PASSED")
print(f"\nCharts saved in: {output_dir}")
for f in sorted(output_dir.glob("*.png")): print(f"  - {f.name}")

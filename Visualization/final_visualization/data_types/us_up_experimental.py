"""
Us-Up Experimental Data Type

Handles loading and displaying Us-Up experimental data from YAML files.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem

from .base_data_type import BaseDataType


class UsUpExperimentalType(BaseDataType):
    """
    Us-Up experimental data from YAML files
    
    This loads shock physics data in the format:
    - Up (particle velocity)
    - Us (shock velocity)
    """
    
    def __init__(self, experimental_data_path: Path):
        super().__init__(name="Us-Up Experiment", category="experimental")
        self.data_path = experimental_data_path
        self._available_cache = {}
        print(f"[UsUpExp] Initialized with path: {experimental_data_path}")
    
    def can_load(self, material_name: str) -> bool:
        """Check if Us-Up data exists for material"""
        if material_name in self._available_cache:
            return self._available_cache[material_name]
        
        # Search for YAML files matching material
        pattern = f"{material_name}*.yaml"
        files = list(self.data_path.glob(pattern))
        
        # Also check case-insensitive
        if not files:
            pattern_lower = f"{material_name.lower()}*.yaml"
            files = [f for f in self.data_path.glob("*.yaml") 
                    if f.stem.lower().startswith(material_name.lower())]
        
        available = len(files) > 0
        self._available_cache[material_name] = available
        
        return available
    
    def load_data(self, material_name: str) -> Dict[str, Any]:
        """Load all Us-Up datasets for material"""
        if material_name in self.data_cache:
            return self.data_cache[material_name]
        
        datasets = []
        pattern = f"{material_name}*.yaml"
        
        # Find matching files
        yaml_files = list(self.data_path.glob(pattern))
        if not yaml_files:
            yaml_files = [f for f in self.data_path.glob("*.yaml") 
                         if f.stem.lower().startswith(material_name.lower())]
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    
                # Check for 'points' structure (current format)
                if data and 'points' in data:
                    points = data['points']
                    if points and len(points) > 0:
                        # Extract Us and Up from points
                        Up_values = [p.get('Up', 0.0) for p in points if 'Up' in p and 'Us' in p]
                        Us_values = [p.get('Us', 0.0) for p in points if 'Up' in p and 'Us' in p]
                        
                        if Up_values and Us_values:
                            datasets.append({
                                'file': yaml_file.name,
                                'Up': Up_values,
                                'Us': Us_values,
                                'metadata': {
                                    'source': data.get('metadata', {}).get('source_file', 'Unknown'),
                                    'notes': data.get('metadata', {}).get('notes', ''),
                                    'material': data.get('metadata', {}).get('material_name', material_name)
                                }
                            })
                
                # Fallback: Check old 'Experimental_data' structure
                elif data and 'Experimental_data' in data:
                    exp_data = data['Experimental_data']
                    if 'Up' in exp_data and 'Us' in exp_data:
                        datasets.append({
                            'file': yaml_file.name,
                            'Up': exp_data['Up'],
                            'Us': exp_data['Us'],
                            'metadata': {
                                'source': exp_data.get('Source', 'Unknown'),
                                'notes': exp_data.get('Notes', '')
                            }
                        })
            except Exception as e:
                print(f"[UsUpExp] Error loading {yaml_file}: {e}")
        
        result = {
            'material': material_name,
            'datasets': datasets,
            'count': len(datasets)
        }
        
        self.data_cache[material_name] = result
        return result
    
    def get_plot_data(self, material_name: str) -> Dict[str, Any]:
        """Get data formatted for plotting"""
        data = self.load_data(material_name)
        
        plot_data = {
            'type': 'scatter',
            'series': []
        }
        
        for i, dataset in enumerate(data['datasets']):
            plot_data['series'].append({
                'x': dataset['Up'],
                'y': dataset['Us'],
                'label': f"{material_name} - {dataset['file']}",
                'marker': 'o',
                'color': None,  # Will be assigned by plot manager
                'metadata': dataset['metadata']
            })
        
        plot_data['xlabel'] = 'Up (Particle Velocity, km/s)'
        plot_data['ylabel'] = 'Us (Shock Velocity, km/s)'
        plot_data['title'] = f'Us-Up Data: {material_name}'
        
        return plot_data
    
    def get_display_widget(self, material_name: str) -> Optional[QWidget]:
        """Get widget to display in data panel"""
        data = self.load_data(material_name)
        
        if data['count'] == 0:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Summary label
        summary = QLabel(f"📊 {data['count']} dataset(s)")
        summary.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(summary)
        
        # Tree view
        tree = QTreeWidget()
        tree.setHeaderLabels(['Dataset', 'Points', 'Source'])
        tree.setMaximumHeight(150)
        
        for i, dataset in enumerate(data['datasets']):
            item = QTreeWidgetItem([
                dataset['file'],
                str(len(dataset['Up'])),
                dataset['metadata']['source']
            ])
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def get_summary(self, material_name: str) -> str:
        """Get text summary"""
        data = self.load_data(material_name)
        total_points = sum(len(d['Up']) for d in data['datasets'])
        return f"{data['count']} datasets, {total_points} data points"

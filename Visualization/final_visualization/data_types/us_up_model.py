"""
Us-Up Model Data Type

Handles loading and displaying Us-Up model parameters from XML files.
Linear model: Us = C0 + S * Up
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout

from .base_data_type import BaseDataType


class UsUpModelType(BaseDataType):
    """
    Us-Up model parameters from XML
    
    Loads model parameters like:
    - C0: Bulk sound speed
    - S: Slope parameter
    - For linear Us-Up relation: Us = C0 + S*Up
    """
    
    def __init__(self, xml_models_path: Path):
        super().__init__(name="Us-Up Model", category="model")
        self.xml_path = xml_models_path
        self._available_cache = {}
        print(f"[UsUpModel] Initialized with path: {xml_models_path}")
    
    def can_load(self, material_name: str) -> bool:
        """Check if Us-Up model exists for material"""
        if material_name in self._available_cache:
            return self._available_cache[material_name]
        
        # Look for XML file
        xml_file = self.xml_path / f"{material_name}.xml"
        if not xml_file.exists():
            # Try case-insensitive
            xml_files = [f for f in self.xml_path.glob("*.xml") 
                        if f.stem.lower() == material_name.lower()]
            xml_file = xml_files[0] if xml_files else None
        
        if not xml_file or not xml_file.exists():
            self._available_cache[material_name] = False
            return False
        
        # Check if Us-Up model exists in XML
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Look for Us-Up model in various locations
            has_usup = False
            
            # Check in Properties
            for prop in root.findall('.//Property'):
                if prop.get('name') in ['Us_Up', 'UsUp', 'Shock_Hugoniot']:
                    has_usup = True
                    break
            
            # Check in Models section
            if not has_usup:
                for model in root.findall('.//Model'):
                    if 'usup' in model.get('type', '').lower():
                        has_usup = True
                        break
            
            self._available_cache[material_name] = has_usup
            return has_usup
            
        except Exception as e:
            print(f"[UsUpModel] Error checking {xml_file}: {e}")
            self._available_cache[material_name] = False
            return False
    
    def load_data(self, material_name: str) -> Dict[str, Any]:
        """Load Us-Up model parameters"""
        if material_name in self.data_cache:
            return self.data_cache[material_name]
        
        xml_file = self.xml_path / f"{material_name}.xml"
        if not xml_file.exists():
            xml_files = [f for f in self.xml_path.glob("*.xml") 
                        if f.stem.lower() == material_name.lower()]
            xml_file = xml_files[0] if xml_files else None
        
        if not xml_file:
            return {'material': material_name, 'parameters': {}, 'found': False}
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            parameters = {}
            
            # Try to find C0 and S parameters
            for prop in root.findall('.//Property'):
                prop_name = prop.get('name', '')
                if 'C0' in prop_name or 'c0' in prop_name.lower():
                    params = prop.find('Parameters')
                    if params is not None:
                        for param in params.findall('Parameter'):
                            if 'C0' in param.get('name', ''):
                                parameters['C0'] = float(param.text)
                
                if 'S' in prop_name or 'slope' in prop_name.lower():
                    params = prop.find('Parameters')
                    if params is not None:
                        for param in params.findall('Parameter'):
                            if param.get('name') == 'S':
                                parameters['S'] = float(param.text)
            
            # If not found, try alternative structure
            if not parameters:
                for model in root.findall('.//Model'):
                    if 'usup' in model.get('type', '').lower():
                        for param in model.findall('.//Parameter'):
                            name = param.get('name')
                            value = param.text
                            if name and value:
                                try:
                                    parameters[name] = float(value)
                                except:
                                    parameters[name] = value
            
            result = {
                'material': material_name,
                'parameters': parameters,
                'found': len(parameters) > 0,
                'model_type': 'Linear' if 'C0' in parameters and 'S' in parameters else 'Unknown'
            }
            
            self.data_cache[material_name] = result
            return result
            
        except Exception as e:
            print(f"[UsUpModel] Error loading {xml_file}: {e}")
            return {'material': material_name, 'parameters': {}, 'found': False}
    
    def get_plot_data(self, material_name: str) -> Dict[str, Any]:
        """Get model curve for plotting"""
        data = self.load_data(material_name)
        
        if not data['found'] or 'C0' not in data['parameters']:
            return {'type': 'line', 'series': []}
        
        C0 = data['parameters'].get('C0', 0)
        S = data['parameters'].get('S', 1)
        
        # Generate model curve
        Up_range = np.linspace(0, 5, 100)  # 0 to 5 km/s
        Us_model = C0 + S * Up_range
        
        plot_data = {
            'type': 'line',
            'series': [{
                'x': Up_range.tolist(),
                'y': Us_model.tolist(),
                'label': f"{material_name} Model (C0={C0:.2f}, S={S:.2f})",
                'linestyle': '-',
                'linewidth': 2,
                'color': None,  # Will be assigned
                'metadata': data['parameters']
            }],
            'xlabel': 'Up (Particle Velocity, km/s)',
            'ylabel': 'Us (Shock Velocity, km/s)',
            'title': f'Us-Up Model: {material_name}'
        }
        
        return plot_data
    
    def get_display_widget(self, material_name: str) -> Optional[QWidget]:
        """Get widget to display model parameters"""
        data = self.load_data(material_name)
        
        if not data['found']:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel(f"📐 {data['model_type']} Model")
        title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Parameters
        form = QFormLayout()
        for param_name, param_value in data['parameters'].items():
            if isinstance(param_value, float):
                value_str = f"{param_value:.4f}"
            else:
                value_str = str(param_value)
            
            label = QLabel(value_str)
            form.addRow(f"{param_name}:", label)
        
        layout.addLayout(form)
        
        # Equation
        if 'C0' in data['parameters'] and 'S' in data['parameters']:
            C0 = data['parameters']['C0']
            S = data['parameters']['S']
            equation = QLabel(f"Us = {C0:.2f} + {S:.2f} × Up")
            equation.setStyleSheet("color: #16a085; font-style: italic; margin-top: 5px;")
            layout.addWidget(equation)
        
        layout.addStretch()
        
        return widget
    
    def get_summary(self, material_name: str) -> str:
        """Get text summary"""
        data = self.load_data(material_name)
        if not data['found']:
            return "No model parameters found"
        
        C0 = data['parameters'].get('C0', 'N/A')
        S = data['parameters'].get('S', 'N/A')
        return f"Linear model: C0={C0}, S={S}"

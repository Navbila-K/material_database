"""
Plot Manager - Handles all plotting logic

Manages plot creation and updates based on:
- Selected materials
- View mode (single, compare, overlay)
- Chart type
- Data types selected
"""

import numpy as np
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[PlotManager] Matplotlib not available")


class PlotManager(QWidget):
    """
    Plot Manager - Creates and updates plots
    
    Modes:
    - Single: One material, detailed view
    - Compare: Multiple materials, side-by-side subplots
    - Overlay: Multiple materials on one plot
    """
    
    plot_clicked = pyqtSignal(str)  # Emitted when plot area is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_mode = "compare"
        self.current_chart_type = "Us-Up (Shock Physics)"
        self.materials_data = {}  # {material_name: {exp_data, model_data}}
        self.material_colors = {}
        
        # Color palette
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ]
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup plot area UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if not MATPLOTLIB_AVAILABLE:
            error_label = QLabel("⚠️ Matplotlib not available\nInstall with: pip install matplotlib")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 50px;")
            layout.addWidget(error_label)
            return
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Add toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Control buttons
        controls = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_plot)
        controls.addWidget(clear_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_plot)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        self.status_label = QLabel("Ready to plot")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        controls.addWidget(self.status_label)
        
        layout.addLayout(controls)
    
    def set_mode(self, mode: str):
        """Set view mode (single, compare, overlay)"""
        self.current_mode = mode
        print(f"[PlotManager] Mode changed to: {mode}")
        self.refresh_plot()
    
    def set_chart_type(self, chart_type: str):
        """Set chart type"""
        self.current_chart_type = chart_type
        print(f"[PlotManager] Chart type changed to: {chart_type}")
        self.refresh_plot()
    
    def add_material_data(self, material_name: str, exp_data: Optional[Dict] = None, 
                         model_data: Optional[Dict] = None, color: Optional[str] = None):
        """Add material data to plot"""
        if material_name not in self.materials_data:
            self.materials_data[material_name] = {}
        
        if exp_data:
            self.materials_data[material_name]['experimental'] = exp_data
        
        if model_data:
            self.materials_data[material_name]['model'] = model_data
        
        # Assign color
        if color:
            self.material_colors[material_name] = color
        elif material_name not in self.material_colors:
            idx = len(self.material_colors) % len(self.color_palette)
            self.material_colors[material_name] = self.color_palette[idx]
        
        print(f"[PlotManager] Added data for {material_name}")
        self.refresh_plot()
    
    def remove_material_data(self, material_name: str):
        """Remove material data"""
        if material_name in self.materials_data:
            del self.materials_data[material_name]
        if material_name in self.material_colors:
            del self.material_colors[material_name]
        
        print(f"[PlotManager] Removed data for {material_name}")
        self.refresh_plot()
    
    def clear_plot(self):
        """Clear all data and plot"""
        self.materials_data.clear()
        self.material_colors.clear()
        self.figure.clear()
        self.canvas.draw()
        self.status_label.setText("Plot cleared")
    
    def refresh_plot(self):
        """Refresh the plot with current data"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        if not self.materials_data:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data to plot\n\nAdd materials to begin',
                   ha='center', va='center', fontsize=14, color='#7f8c8d')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.canvas.draw()
            self.status_label.setText("No data")
            return
        
        # Route to appropriate plotting method
        if self.current_mode == "single":
            self._plot_single_mode()
        elif self.current_mode == "compare":
            self._plot_compare_mode()
        elif self.current_mode == "overlay":
            self._plot_overlay_mode()
        else:
            self._plot_overlay_mode()  # Default
    
    def _plot_single_mode(self):
        """Plot single material in detail"""
        self.figure.clear()
        
        # Get first material
        if not self.materials_data:
            return
        
        material_name = list(self.materials_data.keys())[0]
        data = self.materials_data[material_name]
        color = self.material_colors[material_name]
        
        ax = self.figure.add_subplot(111)
        
        # Plot experimental data
        if 'experimental' in data:
            exp_data = data['experimental']
            if exp_data and 'datasets' in exp_data:
                for i, dataset in enumerate(exp_data['datasets']):
                    Up = dataset.get('Up', [])
                    Us = dataset.get('Us', [])
                    if Up and Us:
                        label = f"Exp: {dataset.get('file', f'Dataset {i+1}')}"
                        ax.plot(Up, Us, 'o', color=color, label=label, markersize=6, alpha=0.7)
        
        # Plot model data
        if 'model' in data:
            model_data = data['model']
            if model_data and 'parameters' in model_data:
                params = model_data['parameters']
                if 'C0' in params and 'S' in params:
                    C0 = params['C0']
                    S = params['S']
                    Up_model = np.linspace(0, 5, 100)
                    Us_model = C0 + S * Up_model
                    ax.plot(Up_model, Us_model, '-', color=color, linewidth=2,
                           label=f"Model: Us = {C0:.2f} + {S:.2f}×Up")
        
        ax.set_xlabel('Up (Particle Velocity, km/s)', fontsize=12)
        ax.set_ylabel('Us (Shock Velocity, km/s)', fontsize=12)
        ax.set_title(f'{material_name} - Us-Up Data', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
        self.status_label.setText(f"Showing: {material_name} (Single mode)")
    
    def _plot_compare_mode(self):
        """Plot materials side-by-side"""
        self.figure.clear()
        
        n_materials = len(self.materials_data)
        
        if n_materials == 0:
            return
        
        # Calculate subplot layout
        if n_materials == 1:
            rows, cols = 1, 1
        elif n_materials == 2:
            rows, cols = 1, 2
        elif n_materials <= 4:
            rows, cols = 2, 2
        elif n_materials <= 6:
            rows, cols = 2, 3
        else:
            rows, cols = 3, 3
        
        for idx, (material_name, data) in enumerate(self.materials_data.items()):
            if idx >= 9:  # Max 9 subplots
                break
            
            ax = self.figure.add_subplot(rows, cols, idx + 1)
            color = self.material_colors[material_name]
            
            # Plot experimental
            if 'experimental' in data:
                exp_data = data['experimental']
                if exp_data and 'datasets' in exp_data:
                    for dataset in exp_data['datasets']:
                        Up = dataset.get('Up', [])
                        Us = dataset.get('Us', [])
                        if Up and Us:
                            ax.plot(Up, Us, 'o', color=color, markersize=4, alpha=0.7)
            
            # Plot model
            if 'model' in data:
                model_data = data['model']
                if model_data and 'parameters' in model_data:
                    params = model_data['parameters']
                    if 'C0' in params and 'S' in params:
                        C0 = params['C0']
                        S = params['S']
                        Up_model = np.linspace(0, 5, 100)
                        Us_model = C0 + S * Up_model
                        ax.plot(Up_model, Us_model, '-', color=color, linewidth=1.5)
            
            ax.set_title(material_name, fontsize=10, fontweight='bold')
            ax.set_xlabel('Up (km/s)', fontsize=9)
            ax.set_ylabel('Us (km/s)', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=8)
        
        self.figure.suptitle('Material Comparison - Us-Up Data', fontsize=12, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()
        self.status_label.setText(f"Comparing {n_materials} materials (Side-by-side)")
    
    def _plot_overlay_mode(self):
        """Plot all materials on one plot"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        legend_items = []
        
        for material_name, data in self.materials_data.items():
            color = self.material_colors[material_name]
            
            # Plot experimental
            if 'experimental' in data:
                exp_data = data['experimental']
                if exp_data and 'datasets' in exp_data:
                    for i, dataset in enumerate(exp_data['datasets']):
                        Up = dataset.get('Up', [])
                        Us = dataset.get('Us', [])
                        if Up and Us:
                            label = f"{material_name} (Exp)" if i == 0 else None
                            line = ax.plot(Up, Us, 'o', color=color, markersize=6,
                                         alpha=0.6, label=label)
                            if label:
                                legend_items.append(line[0])
            
            # Plot model
            if 'model' in data:
                model_data = data['model']
                if model_data and 'parameters' in model_data:
                    params = model_data['parameters']
                    if 'C0' in params and 'S' in params:
                        C0 = params['C0']
                        S = params['S']
                        Up_model = np.linspace(0, 5, 100)
                        Us_model = C0 + S * Up_model
                        line = ax.plot(Up_model, Us_model, '-', color=color, linewidth=2,
                                     label=f"{material_name} (Model)")
                        legend_items.append(line[0])
        
        ax.set_xlabel('Up (Particle Velocity, km/s)', fontsize=12)
        ax.set_ylabel('Us (Shock Velocity, km/s)', fontsize=12)
        ax.set_title('Material Comparison - Us-Up Overlay', fontsize=14, fontweight='bold')
        
        if legend_items:
            ax.legend(loc='best', fontsize=10)
        
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        n_materials = len(self.materials_data)
        self.status_label.setText(f"Overlaying {n_materials} materials")

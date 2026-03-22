"""
EOS Visualization Tab - Advanced Shock Physics Visualization
Combines experimental database data with theoretical model predictions
"""

import sys
import numpy as np
from typing import Optional, Dict, List
import csv
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QRadioButton, QButtonGroup, QFileDialog,
    QMessageBox, QSplitter, QHeaderView, QCompleter, QScrollArea
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from eos_engine import EOSCalculator


class EOSVisualizationTab(QWidget):
    """
    Advanced EOS Visualization Tab with dual data source support:
    - Experimental data from PostgreSQL database
    - Theoretical calculations from user-defined parameters
    """
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.eos_calculator = EOSCalculator(db_manager)
        
        # Current state
        self.current_material = None
        self.experimental_data = None
        self.theoretical_data = None
        self.current_parameters = None
        
        self.init_ui()
        self.load_materials_list()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        
        # Left panel (controls) - wrapped in scroll area
        left_panel_layout = self.create_control_panel()
        
        # Create scroll area for left panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMinimumWidth(370)
        scroll_area.setMaximumWidth(470)
        
        # Create widget to hold the control panel
        left_widget = QWidget()
        left_widget.setLayout(left_panel_layout)
        scroll_area.setWidget(left_widget)
        
        # Style the scroll area
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #95a5a6;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7f8c8d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Right panel (visualization)
        right_panel = self.create_visualization_panel()
        
        # Add panels with splitter for resizing
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        splitter.addWidget(scroll_area)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_control_panel(self) -> QVBoxLayout:
        """Create the left control panel with all input controls."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # ========== Material Selection ==========
        material_group = QGroupBox("📦 Material Selection")
        material_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        material_layout = QVBoxLayout()
        
        material_layout.addWidget(QLabel("Select Material:"))
        self.material_combo = QComboBox()
        self.material_combo.setEditable(True)
        self.material_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_combo.setPlaceholderText("Type to search materials...")
        self.material_combo.currentTextChanged.connect(self.on_material_changed)
        material_layout.addWidget(self.material_combo)
        
        # Material info label
        self.material_info_label = QLabel("No material selected")
        self.material_info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        self.material_info_label.setWordWrap(True)
        material_layout.addWidget(self.material_info_label)
        
        material_group.setLayout(material_layout)
        layout.addWidget(material_group)
        
        # ========== Data Source Selection ==========
        source_group = QGroupBox("📊 Data Source")
        source_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #2ecc71;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        source_layout = QVBoxLayout()
        
        self.source_group_buttons = QButtonGroup()
        self.radio_experimental = QRadioButton("Experimental Only")
        self.radio_theoretical = QRadioButton("Theoretical Only")
        self.radio_both = QRadioButton("Both (Comparison)")
        self.radio_both.setChecked(True)
        
        self.source_group_buttons.addButton(self.radio_experimental, 1)
        self.source_group_buttons.addButton(self.radio_theoretical, 2)
        self.source_group_buttons.addButton(self.radio_both, 3)
        
        source_layout.addWidget(self.radio_experimental)
        source_layout.addWidget(self.radio_theoretical)
        source_layout.addWidget(self.radio_both)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # ========== Model Parameters ==========
        params_group = QGroupBox("⚙️ Model Parameters")
        params_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e67e22;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        params_layout = QVBoxLayout()
        
        # Density (ρ₀)
        params_layout.addWidget(QLabel("ρ₀ - Initial Density (g/cm³):"))
        self.rho0_input = QLineEdit()
        self.rho0_input.setPlaceholderText("Auto-calculated from data")
        params_layout.addWidget(self.rho0_input)
        
        # Bulk sound speed (C₀)
        params_layout.addWidget(QLabel("C₀ - Bulk Sound Speed (km/s):"))
        self.c0_input = QLineEdit()
        self.c0_input.setPlaceholderText("Auto-calculated from fit")
        params_layout.addWidget(self.c0_input)
        
        # Slope constant (s)
        params_layout.addWidget(QLabel("s - Slope Constant:"))
        self.s_input = QLineEdit()
        self.s_input.setPlaceholderText("Auto-calculated from fit")
        params_layout.addWidget(self.s_input)
        
        # R² display
        self.r_squared_label = QLabel("R² = N/A")
        self.r_squared_label.setStyleSheet("color: #2980b9; font-weight: bold; font-size: 12px;")
        params_layout.addWidget(self.r_squared_label)
        
        # Auto-calculate button
        self.auto_calc_btn = QPushButton("🔄 Auto-Calculate from Experimental Data")
        self.auto_calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.auto_calc_btn.clicked.connect(self.auto_calculate_parameters)
        params_layout.addWidget(self.auto_calc_btn)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # ========== Model Selection ==========
        model_group = QGroupBox("🔬 EOS Model Selection")
        model_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #8e44ad;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("Select EOS Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.eos_calculator.get_available_models())
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.model_combo.setToolTip("Choose the Equation of State model to use")
        model_layout.addWidget(self.model_combo)
        
        # Model description
        self.model_description_label = QLabel()
        self.model_description_label.setWordWrap(True)
        self.model_description_label.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 10px; 
            font-style: italic;
            padding: 5px;
            background-color: #ecf0f1;
            border-radius: 3px;
        """)
        model_layout.addWidget(self.model_description_label)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # ========== Calculation Settings ==========
        calc_group = QGroupBox("🔢 Calculation Settings")
        calc_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #34495e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        calc_layout = QVBoxLayout()
        
        calc_layout.addWidget(QLabel("Calculation Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Up Sweep (0-15 km/s)",
            "V/Vo Sweep (1→0)",
            "EOS model (1-15 km/s)"
        ])
        calc_layout.addWidget(self.mode_combo)
        
        calc_layout.addWidget(QLabel("Plot Type:"))
        self.plot_combo = QComboBox()
        self.plot_combo.addItems([
            "Us vs Up (Hugoniot)",
            "P vs Up",
            "P vs V/Vo",
            "V/Vo vs Up"
        ])
        self.plot_combo.currentTextChanged.connect(self.update_plot)
        calc_layout.addWidget(self.plot_combo)
        
        calc_group.setLayout(calc_layout)
        layout.addWidget(calc_group)
        
        # ========== Action Buttons ==========
        self.generate_btn = QPushButton("📊 Generate Visualization")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_visualization)
        layout.addWidget(self.generate_btn)
        
        self.export_plot_btn = QPushButton("💾 Export Plot (PNG/PDF)")
        self.export_plot_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #21618c;
            }
        """)
        self.export_plot_btn.clicked.connect(self.export_plot)
        layout.addWidget(self.export_plot_btn)
        
        self.export_data_btn = QPushButton("📄 Export Data (CSV/XML)")
        self.export_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
        """)
        self.export_data_btn.clicked.connect(self.export_data)
        layout.addWidget(self.export_data_btn)
        
        layout.addStretch()
        
        return layout
    
    def create_visualization_panel(self) -> QVBoxLayout:
        """Create the right visualization panel with plot and table."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # ========== Plot Area ==========
        plot_label = QLabel("📈 Shock Physics Visualization")
        plot_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(plot_label)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # ========== Data Table ==========
        table_label = QLabel("📋 Data Table")
        table_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(table_label)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            "Up (km/s)", "Us (km/s)", "P (GPa)", "V/V₀", "Source"
        ])
        
        # Table styling
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #2c3e50;
            }
        """)
        
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.data_table.setMinimumHeight(250)
        
        layout.addWidget(self.data_table)
        
        # Initialize model description
        self.update_model_description()
        
        return layout
    
    def load_materials_list(self):
        """Load materials from database and populate dropdown."""
        try:
            materials = self.eos_calculator.db.get_materials_with_experimental_data()
            
            if materials:
                self.material_combo.clear()
                self.material_combo.addItems(materials)
                
                # Add autocomplete
                completer = QCompleter(materials)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.material_combo.setCompleter(completer)
                
                self.material_info_label.setText(f"{len(materials)} materials available")
            else:
                self.material_info_label.setText("No experimental data found")
                
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load materials: {e}")
    
    def on_material_changed(self, material_name: str):
        """Handle material selection change."""
        if not material_name:
            return
            
        self.current_material = material_name
        
        # Get dataset count
        try:
            datasets = self.eos_calculator.db.get_experimental_datasets(material_name)
            points = self.eos_calculator.db.get_all_points_for_material(material_name)
            
            info_text = f"Material: {material_name}\n"
            info_text += f"Datasets: {len(datasets)} | Data Points: {len(points)}"
            self.material_info_label.setText(info_text)
            
            # Auto-load and calculate parameters
            self.auto_calculate_parameters()
            
        except Exception as e:
            self.material_info_label.setText(f"Error loading material: {e}")
    
    def update_model_description(self):
        """Update the model description based on current selection"""
        model_name = self.model_combo.currentText()
        descriptions = {
            "Linear Us-Up Hugoniot": "Linear shock velocity-particle velocity relationship: Us = C₀ + s·Up",
            "Quadratic Us-Up Hugoniot": "Quadratic relationship: Us = C₀ + s·Up + q·Up²",
            "Mie-Gruneisen EOS": "Pressure-volume-energy relationship with Gruneisen parameter",
            "Ideal Gas EOS": "Ideal gas equation: P·V = n·R·T"
        }
        description = descriptions.get(model_name, "Select a model to see its description")
        self.model_description_label.setText(description)
    
    def on_model_changed(self):
        """Handle model selection change"""
        self.update_model_description()
        # Update parameter inputs based on model requirements
        model_name = self.model_combo.currentText()
        
        # Show/hide parameter fields based on model
        if model_name == "Quadratic Us-Up Hugoniot":
            # TODO: Add quadratic parameter field if not exists
            pass
        elif model_name == "Mie-Gruneisen EOS":
            # TODO: Add Gruneisen parameter field if not exists
            pass
        
        # Regenerate visualization with new model
        if self.current_material:
            self.update_plot()
    
    def auto_calculate_parameters(self):
        """Auto-calculate C₀, s, and ρ₀ from experimental data."""
        if not self.current_material:
            QMessageBox.warning(self, "No Material", "Please select a material first")
            return
        
        try:
            # Get experimental points
            points = self.eos_calculator.db.get_all_points_for_material(self.current_material)
            
            if not points or len(points) < 2:
                QMessageBox.warning(self, "Insufficient Data", 
                                  "Need at least 2 data points for regression")
                return
            
            # Calculate parameters
            rho0, C0, s, R2 = self.eos_calculator.calculate_parameters_from_data(points)
            
            # Update fields
            self.rho0_input.setText(f"{rho0:.4f}")
            self.c0_input.setText(f"{C0:.4f}")
            self.s_input.setText(f"{s:.4f}")
            self.r_squared_label.setText(f"R² = {R2:.6f}")
            
            # Set color based on R² quality
            if R2 > 0.99:
                color = "#27ae60"  # Green - excellent fit
            elif R2 > 0.95:
                color = "#f39c12"  # Orange - good fit
            else:
                color = "#e74c3c"  # Red - poor fit
            
            self.r_squared_label.setStyleSheet(
                f"color: {color}; font-weight: bold; font-size: 12px;"
            )
            
            QMessageBox.information(
                self, 
                "Parameters Calculated", 
                f"Fitted parameters from {len(points)} experimental points:\n\n"
                f"ρ₀ = {rho0:.4f} g/cm³\n"
                f"C₀ = {C0:.4f} km/s\n"
                f"s = {s:.4f}\n"
                f"R² = {R2:.6f}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to calculate parameters: {e}")
    
    def get_calculation_mode(self) -> str:
        """Get the selected calculation mode."""
        mode_text = self.mode_combo.currentText()
        if "Up Sweep" in mode_text:
            return "Up Sweep"
        elif "V/Vo Sweep" in mode_text:
            return "V/Vo Sweep"
        else:
            return "EOS model"
    
    def generate_visualization(self):
        """Generate the complete visualization with selected data sources."""
        if not self.current_material:
            QMessageBox.warning(self, "No Material", "Please select a material first")
            return
        
        try:
            # Get parameters
            rho0 = float(self.rho0_input.text()) if self.rho0_input.text() else None
            C0 = float(self.c0_input.text()) if self.c0_input.text() else None
            s = float(self.s_input.text()) if self.s_input.text() else None
            mode = self.get_calculation_mode()
            
            # Get data based on source selection
            source_id = self.source_group_buttons.checkedId()
            
            # Get experimental data
            if source_id in [1, 3]:  # Experimental or Both
                self.experimental_data = self.eos_calculator.db.get_all_points_for_material(
                    self.current_material
                )
            else:
                self.experimental_data = None
            
            # Get theoretical data
            if source_id in [2, 3]:  # Theoretical or Both
                if C0 is None or s is None:
                    QMessageBox.warning(
                        self, 
                        "Missing Parameters", 
                        "Please provide C₀ and s values or click Auto-Calculate"
                    )
                    return
                
                # Get rho0 from experimental data if not provided
                if rho0 is None:
                    exp_points = self.eos_calculator.db.get_all_points_for_material(
                        self.current_material
                    )
                    rho0 = exp_points[0]['rho0'] if exp_points else None
                
                if rho0 is None:
                    QMessageBox.warning(self, "Missing Density", 
                                      "Please provide ρ₀ value")
                    return
                
                self.theoretical_data = self.eos_calculator.get_theoretical_results(
                    rho0, C0, s, mode
                )
                self.current_parameters = {'rho0': rho0, 'C0': C0, 's': s}
            else:
                self.theoretical_data = None
            
            # Update plot and table
            self.update_plot()
            self.update_table()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid parameter value: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Visualization Error", f"Failed to generate: {e}")
    
    def update_plot(self):
        """Update the matplotlib plot with current data."""
        self.ax.clear()
        
        if self.experimental_data is None and self.theoretical_data is None:
            self.ax.text(0.5, 0.5, 'No data to display\nClick "Generate Visualization"',
                        ha='center', va='center', fontsize=14, color='gray')
            self.canvas.draw()
            return
        
        plot_type = self.plot_combo.currentText()
        
        # Plot experimental data
        if self.experimental_data:
            exp_up = [p['up'] for p in self.experimental_data if p.get('up') is not None]
            exp_us = [p['us'] for p in self.experimental_data if p.get('us') is not None]
            exp_p = [p['p'] for p in self.experimental_data if p.get('p') is not None]
            exp_v = [p['v_over_v0'] for p in self.experimental_data if p.get('v_over_v0') is not None]
            
            if "Us vs Up" in plot_type:
                self.ax.scatter(exp_up, exp_us, color='red', marker='x', s=80, 
                              linewidths=2, label='Experimental', zorder=3)
                xlabel, ylabel = "Up (km/s)", "Us (km/s)"
                
            elif "P vs Up" in plot_type:
                self.ax.scatter(exp_p, exp_up, color='darkred', marker='o', s=60,
                              label='Experimental', zorder=3)
                xlabel, ylabel = "P (GPa)", "Up (km/s)"
                
            elif "P vs V/Vo" in plot_type:
                self.ax.scatter(exp_p, exp_v, color='darkblue', marker='s', s=60,
                              label='Experimental', zorder=3)
                xlabel, ylabel = "P (GPa)", "V/V₀"
                
            else:  # V/Vo vs Up
                self.ax.scatter(exp_up, exp_v, color='darkgreen', marker='^', s=60,
                              label='Experimental', zorder=3)
                xlabel, ylabel = "Up (km/s)", "V/V₀"
        
        # Plot theoretical data
        if self.theoretical_data:
            theo_up = self.theoretical_data['Up']
            theo_us = self.theoretical_data['Us']
            theo_p = self.theoretical_data['P']
            theo_v = self.theoretical_data['V_ratio']
            
            if "Us vs Up" in plot_type:
                self.ax.plot(theo_up, theo_us, 'b-', linewidth=2.5, 
                           label='Theoretical', zorder=2)
                xlabel, ylabel = "Up (km/s)", "Us (km/s)"
                
            elif "P vs Up" in plot_type:
                self.ax.plot(theo_p, theo_up, 'r-', linewidth=2.5,
                           label='Theoretical', zorder=2)
                xlabel, ylabel = "P (GPa)", "Up (km/s)"
                
            elif "P vs V/Vo" in plot_type:
                self.ax.plot(theo_p, theo_v, 'g-', linewidth=2.5,
                           label='Theoretical', zorder=2)
                xlabel, ylabel = "P (GPa)", "V/V₀"
                
            else:  # V/Vo vs Up
                self.ax.plot(theo_up, theo_v, 'm-', linewidth=2.5,
                           label='Theoretical', zorder=2)
                xlabel, ylabel = "Up (km/s)", "V/V₀"
        
        # Formatting
        self.ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        self.ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        self.ax.set_title(f"{plot_type} - {self.current_material}", 
                         fontsize=14, fontweight='bold', pad=15)
        self.ax.legend(loc='best', fontsize=11, framealpha=0.9)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_table(self):
        """Update the data table with current results."""
        self.data_table.setRowCount(0)
        
        row = 0
        
        # Add experimental data
        if self.experimental_data:
            for point in self.experimental_data:
                self.data_table.insertRow(row)
                self.data_table.setItem(row, 0, QTableWidgetItem(f"{point.get('up', 0):.4f}"))
                self.data_table.setItem(row, 1, QTableWidgetItem(f"{point.get('us', 0):.4f}"))
                self.data_table.setItem(row, 2, QTableWidgetItem(f"{point.get('p', 0):.4f}"))
                self.data_table.setItem(row, 3, QTableWidgetItem(f"{point.get('v_over_v0', 0):.4f}"))
                
                source_item = QTableWidgetItem("Experimental")
                source_item.setBackground(QColor(255, 200, 200))
                self.data_table.setItem(row, 4, source_item)
                row += 1
        
        # Add theoretical data (sample every 10th point to keep table manageable)
        if self.theoretical_data:
            theo_up = self.theoretical_data['Up']
            theo_us = self.theoretical_data['Us']
            theo_p = self.theoretical_data['P']
            theo_v = self.theoretical_data['V_ratio']
            
            step = max(1, len(theo_up) // 50)  # Max 50 theoretical points
            
            for i in range(0, len(theo_up), step):
                self.data_table.insertRow(row)
                self.data_table.setItem(row, 0, QTableWidgetItem(f"{theo_up[i]:.4f}"))
                self.data_table.setItem(row, 1, QTableWidgetItem(f"{theo_us[i]:.4f}"))
                self.data_table.setItem(row, 2, QTableWidgetItem(f"{theo_p[i]:.4f}"))
                self.data_table.setItem(row, 3, QTableWidgetItem(f"{theo_v[i]:.4f}"))
                
                source_item = QTableWidgetItem("Theoretical")
                source_item.setBackground(QColor(200, 200, 255))
                self.data_table.setItem(row, 4, source_item)
                row += 1
    
    def export_plot(self):
        """Export the current plot to PNG or PDF."""
        if self.experimental_data is None and self.theoretical_data is None:
            QMessageBox.warning(self, "No Data", "Generate visualization first")
            return
        
        file_filter = "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg)"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            f"{self.current_material}_eos_plot.png",
            file_filter
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Plot exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def export_data(self):
        """Export table data to CSV or XML."""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "Generate visualization first")
            return
        
        file_filter = "CSV File (*.csv);;XML File (*.xml);;Text File (*.txt)"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"{self.current_material}_eos_data.csv",
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            if "CSV" in selected_filter or "Text" in selected_filter:
                self.export_csv(file_path)
            elif "XML" in selected_filter:
                self.export_xml(file_path)
            
            QMessageBox.information(self, "Success", f"Data exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def export_csv(self, file_path: str):
        """Export data to CSV format."""
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            headers = [
                self.data_table.horizontalHeaderItem(i).text()
                for i in range(self.data_table.columnCount())
            ]
            writer.writerow(headers)
            
            # Write data
            for row in range(self.data_table.rowCount()):
                row_data = [
                    self.data_table.item(row, col).text()
                    for col in range(self.data_table.columnCount())
                ]
                writer.writerow(row_data)
    
    def export_xml(self, file_path: str):
        """Export data to XML format."""
        root = ET.Element("EOS_Data")
        root.set("material", self.current_material)
        
        if self.current_parameters:
            params = ET.SubElement(root, "Parameters")
            ET.SubElement(params, "rho0").text = str(self.current_parameters['rho0'])
            ET.SubElement(params, "C0").text = str(self.current_parameters['C0'])
            ET.SubElement(params, "s").text = str(self.current_parameters['s'])
        
        data_section = ET.SubElement(root, "DataPoints")
        
        for row in range(self.data_table.rowCount()):
            point = ET.SubElement(data_section, "Point")
            point.set("index", str(row + 1))
            
            ET.SubElement(point, "Up").text = self.data_table.item(row, 0).text()
            ET.SubElement(point, "Us").text = self.data_table.item(row, 1).text()
            ET.SubElement(point, "P").text = self.data_table.item(row, 2).text()
            ET.SubElement(point, "V_ratio").text = self.data_table.item(row, 3).text()
            ET.SubElement(point, "Source").text = self.data_table.item(row, 4).text()
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

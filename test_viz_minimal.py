#!/usr/bin/env python3
"""
Minimal test of Visualization Tab to diagnose issues
"""

import sys
from pathlib import Path

# Set matplotlib backend BEFORE anything else
import matplotlib
print(f"Default backend: {matplotlib.get_backend()}")
matplotlib.use('QtAgg', force=True)
print(f"Forced backend: {matplotlib.get_backend()}")

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MinimalVizTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Visualization Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout.addWidget(self.canvas)
        
        # Add test button
        self.test_btn = QPushButton("Generate Test Plot")
        self.test_btn.clicked.connect(self.test_plot)
        layout.addWidget(self.test_btn)
        
        print("Minimal test window created successfully!")
        
    def test_plot(self):
        print("Test plot button clicked!")
        try:
            # Clear previous plot
            self.ax.clear()
            
            # Generate test data
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            
            # Plot
            self.ax.plot(x, y, 'b-', linewidth=2, label='sin(x)')
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_title('Test Plot')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Draw
            self.canvas.draw()
            print("Plot generated successfully!")
            
        except Exception as e:
            print(f"ERROR generating plot: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Starting minimal visualization test...")
    
    app = QApplication(sys.argv)
    window = MinimalVizTest()
    window.show()
    
    print("Window shown, entering event loop...")
    sys.exit(app.exec())

#!/usr/bin/env python3
"""
Materials Database GUI Launcher

Run the PyQt6 graphical interface for the Materials Database.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Fix Qt plugin path issue on macOS/Conda
# This ensures PyQt6 can find platform plugins (cocoa, etc.)
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    qt_plugin_path = pyqt6_path / "Qt6" / "plugins"
    if qt_plugin_path.exists():
        os.environ['QT_PLUGIN_PATH'] = str(qt_plugin_path)
        print(f"DEBUG: Set QT_PLUGIN_PATH to {qt_plugin_path}")
except Exception as e:
    print(f"WARNING: Could not set QT_PLUGIN_PATH: {e}")

# CRITICAL: Set matplotlib backend BEFORE any GUI imports
# This prevents backend conflicts between macOS default and QtAgg
try:
    import matplotlib
    current_backend = matplotlib.get_backend()
    print(f"DEBUG: Matplotlib default backend: {current_backend}")
    matplotlib.use('QtAgg', force=True)
    print(f"DEBUG: Matplotlib backend changed to: {matplotlib.get_backend()}")
except Exception as e:
    print(f"WARNING: Could not set matplotlib backend: {e}")

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
except ImportError:
    print("ERROR: PyQt6 is not installed.")
    print("Install it with: pip install PyQt6")
    sys.exit(1)

try:
    from gui.main_window import MainWindow
except ImportError as e:
    print(f"ERROR: Failed to import GUI components: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)


def main():
    """Launch the GUI application."""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Materials Database")
    app.setOrganizationName("Materials Research")
    app.setOrganizationDomain("materials-db.local")
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run event loop
        sys.exit(app.exec())
        
    except Exception as e:
        # Show error dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText("Failed to start application")
        msg.setDetailedText(str(e))
        msg.exec()
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Main entry point for the application.
"""
import sys
import os

# Definir os diretórios base corretamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYZ_DIR = os.path.join(BASE_DIR, "pyz")

for path in [BASE_DIR, PYZ_DIR]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

import ctypes
import atexit
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from core.logger import logger
from core.stealth_manager import stealth_manager
from core.process_randomizer import process_randomizer

sys.dont_write_bytecode = True

def is_admin():
    """Check if the application is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def show_admin_warning():
    """Show a warning message if the application is not running as admin."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle('Admin Rights Required')
    msg.setText('This application may not work correctly without administrator privileges.')
    msg.setInformativeText('Please run the application as administrator for full functionality.')
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    return msg.exec()

def main():
    try:
        stealth_manager.randomize_execution_timing()
        process_randomizer.apply_all_randomizations()
        atexit.register(process_randomizer.cleanup_temp_files)
    except Exception as e:
        logger.log(f'Failed to apply stealth features: {e}', level=30)
        
    logger.log('Application started.')
    app = QApplication(sys.argv)
    
    if not is_admin():
        logger.log('Application not running as admin.', level=30)
        show_admin_warning()
        
    window = MainWindow()
    stealth_settings = stealth_manager.get_stealth_settings()
    window.setWindowTitle(stealth_settings.get('window_title', 'Application'))
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
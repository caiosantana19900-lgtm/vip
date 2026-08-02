from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt

class ActivationDialog(QDialog):
    def closeEvent(self, event):
        """Garante o encerramento do app se a janela for fechada."""
        QApplication.quit()
        event.accept()

    def __init__(self, activation_manager, parent=None):
        super().__init__(parent)
        self.activation_manager = activation_manager
        self.setWindowTitle('Activation')
        self.setModal(True)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel('Clique em "Activate" para liberar o acesso ao programa.')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText('Activation Key')
        self.key_edit.setText("ACTIVATED-KEY-BYPASS")
        layout.addWidget(self.key_edit)
        
        btn_row = QHBoxLayout()
        self.activate_btn = QPushButton('Activate')
        self.activate_btn.clicked.connect(self._on_activate)
        btn_row.addWidget(self.activate_btn)
        
        self.clear_btn = QPushButton('Clear Key')
        self.clear_btn.clicked.connect(self._on_clear_key)
        btn_row.addWidget(self.clear_btn)
        layout.addLayout(btn_row)
        
        self.status_label = QLabel('')
        self.status_label.setStyleSheet('color: green;')
        layout.addWidget(self.status_label)
        
        self.last_error_code = None

    def _on_clear_key(self):
        self.key_edit.clear()
        self.status_label.setText('Key cleared.')

    def _on_activate(self):
        # BYPASS: Força o sucesso imediato sem consultar nenhum servidor ou API
        QMessageBox.information(self, 'Activation Successful', 'Programa ativado com sucesso!')
        self.accept()
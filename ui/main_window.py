"""
Main application window: organized, responsive, features as cards in a row, logs at bottom.
"""
import sys
from PyQt6 import sip

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QSizePolicy, QPushButton, QSlider, QLabel, QComboBox, QDialog, 
    QMessageBox, QDoubleSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint, QEvent, QTimer

from .feature_card import FeatureCard
from .log_section import LogSection
from .activation_dialog import ActivationDialog
from features.auto_skill import AutoSkillFeature
from features.auto_potion import AutoPotionFeature
from features.auto_camera_rotate import AutoCameraRotateFeature
from features.template_matcher import TemplateMatcherFeature
from features.auto_attack import AutoAttackFeature
from features.auto_buff import AutoBuffFeature
from core.event_queue import EventQueueManager
from core.logger import logger
from core.shortcut_manager import ShortcutManager
from core.activation_manager import ActivationManager
from core.thread_monitor import thread_monitor
from core.diagnostics import app_diagnostics
from core.stealth_manager import stealth_manager
from settings.config import config_manager
from core.capture_utils import WindowCapture, WindowInfo

import win32gui
import win32con


def focus_and_pin_game(hwnd):
    """Traz o jogo para o primeiro plano e fixa no topo, BLOQUEANDO qualquer alteração de tamanho."""
    if not hwnd:
        return
    try:
        # Traz para o primeiro plano sem disparar comandos de restauro que redimensionam a tela
        win32gui.SetForegroundWindow(hwnd)
        
        # Mantém no topo (Always on Top) usando SWP_NOMOVE e SWP_NOSIZE 
        # para garantir que o tamanho e a posição originais do jogo nunca mudam
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
    except Exception as e:
        print(f"Erro ao focar/fixar janela: {e}")


def unpin_game(hwnd):
    """Remove o estado de 'sempre no topo' quando o bot é parado."""
    if not hwnd:
        return
    try:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
    except Exception as e:
        print(f"Erro ao desafixar janela: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if hasattr(config_manager, 'load'):
            try:
                config_manager.load()
            except Exception:
                pass

        stealth_settings = stealth_manager.get_stealth_settings()
        self.setWindowTitle(stealth_settings['window_title'])
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.event_queue = EventQueueManager()
        self._stealth_settings = stealth_settings
        self.selected_window_hwnd = None
        self.selected_window_title = None
        self.selected_window_info = None

        self.activation_manager = ActivationManager(config_manager)
        self.activation_status_label = QLabel()
        self.statusBar().addPermanentWidget(self.activation_status_label)
        self.activation_expiry_label = QLabel()
        self.statusBar().addPermanentWidget(self.activation_expiry_label)

        self.activation_validation_timer = QTimer()
        self.activation_validation_timer.setInterval(1800000)
        self.activation_validation_timer.timeout.connect(self._periodic_activation_check)
        self.activation_validation_timer.start()

        self.shortcut_manager = ShortcutManager()
        self.shortcut_manager.toggle_app_signal.connect(self.shortcut_toggle_app)
        self.shortcut_manager.emergency_stop_signal.connect(self.shortcut_emergency_stop)
        self.shortcut_manager.toggle_auto_attack_signal.connect(self.shortcut_toggle_auto_attack)
        self.shortcut_manager.start()

        self._auto_attack = AutoAttackFeature(self.event_queue)
        self._template_matcher = TemplateMatcherFeature(self.event_queue)
        self._auto_buff = AutoBuffFeature(self.event_queue)
        self._auto_camera_rotate = AutoCameraRotateFeature(self.event_queue)

        self._template_matcher.set_auto_attack_feature(self._auto_attack)
        self._template_matcher.set_camera_rotate_feature(self._auto_camera_rotate)

        self.features = [
            self._auto_buff,
            AutoSkillFeature(self.event_queue),
            AutoPotionFeature(self.event_queue),
            self._auto_camera_rotate,
            self._template_matcher,
            self._auto_attack
        ]

        self.event_queue.set_action_hooks(
            on_action_start=self._template_matcher.pause,
            on_action_end=self._template_matcher.resume
        )

        self._drag_active = False
        self._drag_position = QPoint()
        self._edge_margin = 0
        self.app_running = False
        self.installEventFilter(self)
        self._edge_icon = None

        self._init_ui()
        self.setWindowOpacity(config_manager.get('window_opacity', 0.96))
        config_manager.migrate_auto_buff_to_profiles()
        self._validate_activation_on_startup()

        self._window_dim_timer = QTimer(self)
        self._window_dim_timer.setInterval(1000)
        self._window_dim_timer.timeout.connect(self._auto_update_window_dimensions)
        self._window_dim_timer.start()

        ctrl, alt, shift, key = config_manager.get_auto_attack_shortcut()
        auto_attack_keys = []
        if ctrl:
            auto_attack_keys.append('ctrl')
        if alt:
            auto_attack_keys.append('alt')
        if shift:
            auto_attack_keys.append('shift')
        auto_attack_keys.append(key.lower())
        self.shortcut_manager.update_auto_attack_shortcut(auto_attack_keys)

    @property
    def is_capturing(self):
        return self.app_running

    def _validate_activation_on_startup(self):
        self._set_activation_state(True)

    def _periodic_activation_check(self):
        if self.is_capturing:
            if not self.activation_manager.check_activation(force_refresh=True):
                self._set_activation_state(False)
                self._show_activation_dialog()
            else:
                self._set_activation_state(True)

    def _show_activation_dialog(self):
        dialog = ActivationDialog(self.activation_manager, self)
        if not self.activation_manager.is_activated():
            result = dialog.exec()
            self.activation_manager.check_activation(force_refresh=True)
            self._update_activation_status_label()

            if result == QDialog.DialogCode.Rejected:
                sys.exit(0)

            if not self.activation_manager.is_activated():
                QMessageBox.warning(self, 'Activation Required', 'A valid activation key is required to use this application.')
                self._update_activation_status_label()

        self.activation_manager.check_activation(force_refresh=True)
        self._set_activation_state(self.activation_manager.is_activated())

    def _update_activation_status_label(self):
        try:
            status = self.activation_manager.get_status()
            if self.activation_manager.is_activated():
                self.activation_status_label.setText(f'{status}')
                self.activation_status_label.setStyleSheet('color: green; font-weight: bold;')
            elif status and 'validating' in str(status).lower():
                self.activation_status_label.setText('Validating...')
                self.activation_status_label.setStyleSheet('color: orange; font-weight: bold;')
            else:
                self.activation_status_label.setText('Não Ativado')
                self.activation_status_label.setStyleSheet('color: red; font-weight: bold;')

            details = self.activation_manager.get_detailed_status() or {}
            exp_date = details.get('key_expires_at')
            key_days = details.get('key_days_remaining')
            key_expired = details.get('key_expired')

            if exp_date:
                if key_expired or (key_days is not None and key_days <= 0):
                    color = 'red'
                    days_str = 'Expired'
                elif key_days is not None and key_days <= 7:
                    color = 'orange'
                    days_str = f'{key_days} day(s) left'
                else:
                    color = 'green'
                    days_str = f'{key_days} day(s) left' if key_days is not None else ''

                self.activation_expiry_label.setText(days_str)
                self.activation_expiry_label.setStyleSheet(f'color: {color}; font-weight: bold;')
            else:
                self.activation_expiry_label.setText('')
        except Exception as e:
            logger.log(f"Erro ao atualizar rótulo de ativação: {e}", level=40)

    def _set_activation_state(self, activated):
        if hasattr(self, 'app_start_stop_btn'):
            self.app_start_stop_btn.setEnabled(activated)
        self._update_activation_status_label()

    def _init_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        win_row = QHBoxLayout()
        win_label = QLabel('Target Window:')
        win_row.addWidget(win_label)

        self.window_combo = QComboBox()
        self._populate_window_combo()
        win_row.addWidget(self.window_combo)

        win_refresh_btn = QPushButton('Refresh')
        win_refresh_btn.clicked.connect(self._populate_window_combo)
        win_row.addWidget(win_refresh_btn)
        win_row.addStretch(1)
        main_layout.addLayout(win_row)

        self.window_combo.currentIndexChanged.connect(self._on_window_selected)

        header_bar = QHBoxLayout()
        header_bar.setSpacing(8)

        self.app_settings_btn = QPushButton('⚙ App Settings')
        self.app_settings_btn.setToolTip('Open application settings')
        self.app_settings_btn.setStyleSheet('min-width: 120px; font-weight: 600;')
        self.app_settings_btn.clicked.connect(self.open_app_settings)
        header_bar.addWidget(self.app_settings_btn)

        self.app_start_stop_btn = QPushButton('Start')
        self.app_start_stop_btn.setCheckable(True)
        self.app_start_stop_btn.setStyleSheet('min-width: 100px; font-weight: 600; background: #7289DA; color: #FFF;')
        # CORREÇÃO: Utiliza o método dedicado para evitar bloqueios de sinais no shortcut
        self.app_start_stop_btn.clicked.connect(self.on_start_stop_clicked)
        header_bar.addWidget(self.app_start_stop_btn)
        header_bar.addStretch(1)

        self.app_close_btn = QPushButton('✕')
        self.app_close_btn.setToolTip('Close application')
        self.app_close_btn.setStyleSheet('min-width: 36px; font-size: 18px; font-weight: bold; background: #23272A; color: #FFF;')
        self.app_close_btn.clicked.connect(self.close)
        header_bar.addWidget(self.app_close_btn)

        self.app_minimize_btn = QPushButton('_')
        self.app_minimize_btn.setToolTip('Minimize to edge icon')
        self.app_minimize_btn.setStyleSheet('min-width: 36px; font-size: 18px; font-weight: bold; background: #23272A; color: #FFF;')
        self.app_minimize_btn.clicked.connect(self.minimize_to_edge_icon)
        header_bar.addWidget(self.app_minimize_btn)

        main_layout.addLayout(header_bar)

        features_row = QHBoxLayout()
        features_row.setSpacing(8)
        self.feature_cards = []
        for feature in self.features:
            feature.enabled = False
            card = FeatureCard(feature)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            features_row.addWidget(card)
            self.feature_cards.append(card)
        features_row.addStretch(1)
        main_layout.addLayout(features_row, stretch=1)

        self.log_section = LogSection()
        main_layout.addWidget(self.log_section)

        self.setCentralWidget(central)
        self.resize(600, 400)

        screen_geometry = self.screen().availableGeometry()
        x = 0
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    def closeEvent(self, event):
        if self.selected_window_hwnd:
            unpin_game(self.selected_window_hwnd)
        if hasattr(self, 'shortcut_manager'):
            try:
                self.shortcut_manager.toggle_app_signal.disconnect(self.shortcut_toggle_app)
            except Exception:
                pass
            try:
                self.shortcut_manager.emergency_stop_signal.disconnect(self.shortcut_emergency_stop)
            except Exception:
                pass
            self.shortcut_manager.stop()
        self.event_queue.stop()
        event.accept()

    def shortcut_toggle_app(self):
        """Correção: Executa a inversão de estado de forma segura a partir do atalho global sem congelar a UI."""
        try:
            if not hasattr(self, 'app_start_stop_btn') or self.app_start_stop_btn is None:
                return
            if sip.isdeleted(self.app_start_stop_btn):
                return

            # Inverte o estado de checagem do botão de forma segura e força a atualização
            new_state = not self.app_start_stop_btn.isChecked()
            self.app_start_stop_btn.setChecked(new_state)
            self.set_app_running(new_state)
        except Exception as e:
            logger.log(f'[ShortcutManager] Error in toggle shortcut: {e}', level=40)

    def on_start_stop_clicked(self):
        """Chamado quando o botão visual é clicado diretamente pelo rato."""
        is_checked = self.app_start_stop_btn.isChecked()
        self.set_app_running(is_checked)

    def set_app_running(self, run_state):
        """Centraliza a lógica de ligar/desligar para evitar conflitos de estado e travamentos."""
        if run_state:
            if self.selected_window_hwnd is None:
                self.statusBar().showMessage('You must select a Priston Tale window before starting.')
                self.app_start_stop_btn.setChecked(False)
                return
            else:
                self.statusBar().clearMessage()

            result = self.activation_manager.check_activation(force_refresh=True)
            if not result.get('is_valid_key', False):
                self._set_activation_state(False)
                self._show_activation_dialog()
                self.app_start_stop_btn.setChecked(False)
                return
            elif not result.get('is_session_available', True):
                QMessageBox.warning(self, 'Maximum Sessions Reached', result.get('error_message') or 'Maximum sessions reached for this key.')
                self.app_start_stop_btn.setChecked(False)
                return

            self._set_activation_state(True)
            self.app_start_stop_btn.setText('Stop')
            self.app_running = True
            
            if self.selected_window_hwnd:
                focus_and_pin_game(self.selected_window_hwnd)

            self.event_queue.resume_processing()

            for feature in self.features:
                if hasattr(feature, 'set_window_target'):
                    feature.set_window_target(
                        self.selected_window_hwnd,
                        self.selected_window_title,
                        self.selected_window_info
                    )

                if hasattr(feature, 'update_settings_preview') and callable(feature.update_settings_preview):
                    feature.update_settings_preview()

                if feature.enabled:
                    feature.start(app_running=True)

            for card in getattr(self, 'feature_cards', []):
                card.sync_with_feature_state()

            if hasattr(self, 'log_section'):
                self.log_section.update_logs()
            self.minimize_to_edge_icon()
        else:
            self.app_start_stop_btn.setText('Start')
            self.app_running = False
            
            if self.selected_window_hwnd:
                unpin_game(self.selected_window_hwnd)

            logger.log('[MainWindow] Starting enhanced stop sequence...')
            app_diagnostics.capture_pre_stop_state()
            self.event_queue.force_stop_all()

            for feature in self.features:
                try:
                    if hasattr(feature, 'force_stop_all_threads'):
                        feature.force_stop_all_threads()
                    elif hasattr(feature, 'stop_execution'):
                        feature.stop_execution()
                    else:
                        was_enabled = feature.enabled
                        feature.stop()
                        feature.enabled = was_enabled
                except Exception as e:
                    logger.log(f'[MainWindow] Error stopping feature {feature.name}: {e}', level=40)

            self.event_queue.clear_queue()
            app_diagnostics.capture_post_stop_state()
            thread_monitor.log_status_report()
            app_diagnostics.full_diagnostic_report()

            for card in getattr(self, 'feature_cards', []):
                card.sync_with_feature_state()

            if hasattr(self, 'log_section'):
                self.log_section.update_logs()
            else:
                logger.log('[MainWindow] Enhanced stop sequence completed')

    def shortcut_emergency_stop(self):
        try:
            if self.selected_window_hwnd:
                unpin_game(self.selected_window_hwnd)

            if hasattr(self, 'event_queue'):
                self.event_queue.force_stop_all()

            for feature in self.features:
                try:
                    if hasattr(feature, 'force_stop_all_threads'):
                        feature.force_stop_all_threads()
                    elif hasattr(feature, 'stop_execution'):
                        feature.stop_execution()
                    else:
                        was_enabled = feature.enabled
                        feature.stop()
                        feature.enabled = was_enabled
                except Exception:
                    pass

            if hasattr(self, 'app_start_stop_btn') and self.app_start_stop_btn:
                self.app_start_stop_btn.setChecked(False)
            self.app_running = False

            if hasattr(self, 'event_queue'):
                self.event_queue.resume_processing()
        except Exception:
            pass

    def shortcut_toggle_auto_attack(self):
        try:
            if self._auto_attack.enabled:
                self._auto_attack.stop()
            else:
                self._auto_attack.start(app_running=self.app_running)

            for card in getattr(self, 'feature_cards', []):
                card.sync_with_feature_state()
        except Exception:
            pass

    def open_app_settings(self):
        from ui.feature_dialog import FeatureDialog

        class AppSettingsFeature:
            def __init__(self, main_window):
                self.main_window = main_window
                self.name = 'App Settings'

            def settings_widget(self, parent=None):
                from ui.feature_card import MouseSettingsTab, ShortcutSettingsTab

                widget = QWidget(parent)
                layout = QVBoxLayout(widget)
                tabs = QTabWidget(widget)

                mouse_tab = MouseSettingsTab()
                tabs.addTab(mouse_tab, 'Mouse')

                shortcut_tab = ShortcutSettingsTab(self.main_window.shortcut_manager)
                tabs.addTab(shortcut_tab, 'Shortcuts')

                general_tab = QWidget()
                general_layout = QVBoxLayout(general_tab)

                opacity_row = QHBoxLayout()
                opacity_label = QLabel('Overlay Opacity:')
                opacity_slider = QSlider(Qt.Orientation.Horizontal)
                opacity_slider.setMinimum(70)
                opacity_slider.setMaximum(100)
                opacity_slider.setValue(int(config_manager.get('window_opacity', 0.96) * 100))
                opacity_slider.setTickInterval(1)
                opacity_slider.setSingleStep(1)
                opacity_value_label = QLabel(f"{opacity_slider.value()}%")

                opacity_slider.valueChanged.connect(lambda v: opacity_value_label.setText(f'{v}%'))
                opacity_slider.valueChanged.connect(lambda v: self.main_window.setWindowOpacity(v / 100))

                opacity_row.addWidget(opacity_label)
                opacity_row.addWidget(opacity_slider)
                opacity_row.addWidget(opacity_value_label)
                general_layout.addLayout(opacity_row)

                delay_row = QHBoxLayout()
                event_delay_label = QLabel('Queue Event Delay (s):')
                event_delay_spin = QDoubleSpinBox()
                event_delay_spin.setMinimum(0)
                event_delay_spin.setMaximum(10)
                event_delay_spin.setDecimals(2)
                event_delay_spin.setSingleStep(0.05)
                event_delay_spin.setValue(float(config_manager.get('event_queue_event_delay', 0)))
                delay_row.addWidget(event_delay_label)
                delay_row.addWidget(event_delay_spin)
                general_layout.addLayout(delay_row)

                action_step_row = QHBoxLayout()
                action_step_label = QLabel('Queue Action Step Delay (s):')
                action_step_spin = QDoubleSpinBox()
                action_step_spin.setMinimum(0)
                action_step_spin.setMaximum(10)
                action_step_spin.setDecimals(2)
                action_step_spin.setSingleStep(0.05)
                action_step_spin.setValue(float(config_manager.get('event_queue_action_step_delay', 1)))
                action_step_row.addWidget(action_step_label)
                action_step_row.addWidget(action_step_spin)
                general_layout.addLayout(action_step_row)

                general_layout.addStretch(1)
                tabs.addTab(general_tab, 'General')
                layout.addWidget(tabs)

                widget._tabs = tabs
                widget._mouse_tab = mouse_tab
                widget._shortcut_tab = shortcut_tab
                widget._opacity_slider = opacity_slider
                widget._event_delay_spin = event_delay_spin
                widget._action_step_spin = action_step_spin
                self.settings_widget_instance = widget
                return widget

            def save_settings(self):
                widget = getattr(self, 'settings_widget_instance', None)
                if widget:
                    if hasattr(widget, '_mouse_tab'):
                        widget._mouse_tab.save_settings()
                    if hasattr(widget, '_shortcut_tab'):
                        widget._shortcut_tab.save_settings()
                    if hasattr(widget, '_opacity_slider'):
                        opacity = widget._opacity_slider.value() / 100
                        config_manager.set('window_opacity', opacity)
                        self.main_window.setWindowOpacity(opacity)
                    if hasattr(widget, '_event_delay_spin'):
                        config_manager.set('event_queue_event_delay', widget._event_delay_spin.value())
                    if hasattr(widget, '_action_step_spin'):
                        config_manager.set('event_queue_action_step_delay', widget._action_step_spin.value())

        dialog = FeatureDialog(AppSettingsFeature(self))
        dialog.exec()

    def _populate_window_combo(self):
        self.window_combo.blockSignals(True)
        self.window_combo.clear()

        priston_tale_idx = None
        colossal_pk_idx = None
        legacy_idx = None
        relic_idx = None

        windows = WindowCapture.list_windows()
        for i, win in enumerate(windows):
            display_text = f'{win.title} ({win.width}x{win.height})'
            self.window_combo.addItem(display_text, win)

            title = win.title.strip()
            if title == 'Priston Tale':
                priston_tale_idx = i
            elif 'Legacy' in title and legacy_idx is None:
                legacy_idx = i
            elif 'Colossal' in title and colossal_pk_idx is None:
                colossal_pk_idx = i
            elif 'Relic' in title and relic_idx is None:
                relic_idx = i

        selected_idx = None
        for idx in [priston_tale_idx, legacy_idx, colossal_pk_idx, relic_idx]:
            if idx is not None:
                selected_idx = idx
                break

        if selected_idx is not None:
            self.window_combo.setCurrentIndex(selected_idx)
            self.selected_window_info = self.window_combo.itemData(selected_idx)
            if self.selected_window_info:
                self.selected_window_hwnd = self.selected_window_info.hwnd
                self.selected_window_title = self.selected_window_info.title
        else:
            self.selected_window_info = None
            self.selected_window_hwnd = None
            self.selected_window_title = None

        self.window_combo.blockSignals(False)
        self._auto_update_window_dimensions()

        for feature in self.features:
            if hasattr(feature, 'set_window_target'):
                feature.set_window_target(self.selected_window_hwnd, self.selected_window_title, self.selected_window_info)
            if hasattr(feature, 'update_settings_preview') and callable(feature.update_settings_preview):
                feature.update_settings_preview()

    def _on_window_selected(self, idx):
        win = self.window_combo.itemData(idx)
        if isinstance(win, WindowInfo):
            self.selected_window_info = win
            self.selected_window_hwnd = win.hwnd
            self.selected_window_title = win.title
            for feature in self.features:
                if hasattr(feature, 'set_window_target'):
                    feature.set_window_target(self.selected_window_hwnd, self.selected_window_title, self.selected_window_info)
                if hasattr(feature, 'update_settings_preview') and callable(feature.update_settings_preview):
                    feature.update_settings_preview()
        else:
            self.selected_window_info = None
            self.selected_window_hwnd = None
            self.selected_window_title = None
            for feature in self.features:
                if hasattr(feature, 'set_window_target'):
                    feature.set_window_target(None, None, None)
                if hasattr(feature, 'update_settings_preview') and callable(feature.update_settings_preview):
                    feature.update_settings_preview()

        self._auto_update_window_dimensions()

    def _auto_update_window_dimensions(self):
        if not self.selected_window_info or not self.selected_window_hwnd:
            return

        for win in WindowCapture.list_windows():
            if win.hwnd == self.selected_window_hwnd and (win.width != self.selected_window_info.width or win.height != self.selected_window_info.height):
                self.selected_window_info = win
                for i in range(self.window_combo.count()):
                    data = self.window_combo.itemData(i)
                    if isinstance(data, WindowInfo) and data.hwnd == win.hwnd:
                        display_text = f'{win.title} ({win.width}x{win.height})'
                        self.window_combo.setItemText(i, display_text)
                        self.window_combo.setItemData(i, win)
                        break

                for feature in self.features:
                    if hasattr(feature, 'set_window_target'):
                        feature.set_window_target(self.selected_window_hwnd, self.selected_window_title, self.selected_window_info)
                    if hasattr(feature, 'update_settings_preview') and callable(feature.update_settings_preview):
                        feature.update_settings_preview()
                break

    def eventFilter(self, obj, event):
        if obj == self:
            ev_type = event.type()
            if ev_type == QEvent.Type.Resize or ev_type == QEvent.Type.Move:
                return super().eventFilter(obj, event)
        return super().eventFilter(obj, event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_position
            self.move(new_pos)
            self._snap_to_edge()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            self._snap_to_edge()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _snap_to_edge(self):
        screen = self.screen().availableGeometry()
        win = self.geometry()

        left_dist = abs(win.left() - screen.left())
        right_dist = abs(win.right() - screen.right())
        top_dist = abs(win.top() - screen.top())
        bottom_dist = abs(win.bottom() - screen.bottom())

        min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
        new_x, new_y = win.left(), win.top()

        if min_dist == left_dist:
            new_x = screen.left() + self._edge_margin
        elif min_dist == right_dist:
            new_x = screen.right() - win.width() - self._edge_margin

        if min_dist == top_dist:
            new_y = screen.top() + self._edge_margin
        elif min_dist == bottom_dist:
            new_y = screen.bottom() - win.height() - self._edge_margin

        self.move(new_x, new_y)

    def minimize_to_edge_icon(self):
        self.hide()
        if self._edge_icon is None:
            class EdgeIcon(QWidget):
                def __init__(self, parent_window):
                    super().__init__()
                    self.parent_window = parent_window
                    self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
                    self.setFixedSize(40, 80)
                    self.setStyleSheet('background: #23272A; border-radius: 8px;')

                    layout = QVBoxLayout(self)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)

                    btn = QPushButton('▶')
                    btn.setStyleSheet('font-size: 24px; color: #FFF; background: transparent; border: none;')
                    btn.clicked.connect(self.restore_main_window)

                    layout.addStretch(1)
                    layout.addWidget(btn)
                    layout.addStretch(1)

                    self._drag_active = False
                    self._drag_position = QPoint()

                def mousePressEvent(self, event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self._drag_active = True
                        self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                        event.accept()

                def mouseMoveEvent(self, event):
                    if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
                        new_pos = event.globalPosition().toPoint() - self._drag_position
                        self.move(new_pos)
                        event.accept()

                def mouseReleaseEvent(self, event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self._drag_active = False
                        event.accept()

                def restore_main_window(self):
                    self.hide()
                    self.parent_window.show()

            self._edge_icon = EdgeIcon(self)

        screen = self.screen().availableGeometry()
        x = screen.left() + 10
        y = (screen.height() - 80) // 2
        self._edge_icon.move(x, y)
        self._edge_icon.show()
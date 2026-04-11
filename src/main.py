import os
import sys
import time


def _preload_model():
    """Load the CUDA model before PyQt5 to avoid GPU context segfault."""
    from utils import ConfigManager
    from transcription import create_local_model

    ConfigManager.initialize()
    model_options = ConfigManager.get_config_section('model_options')
    if ConfigManager.config_file_exists() and not model_options.get('use_api'):
        model = create_local_model()
    else:
        model = None
    ConfigManager._instance = None
    return model


def _run_app(preloaded_model=None):
    from audioplayer import AudioPlayer
    from pynput.keyboard import Controller
    from PyQt5.QtCore import QObject, QProcess
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox

    from key_listener import KeyListener
    from result_thread import ResultThread
    from ui.main_window import MainWindow
    from ui.settings_window import SettingsWindow
    from ui.status_window import StatusWindow
    from transcription import create_local_model
    from input_simulation import InputSimulator
    from utils import ConfigManager

    class WhisperWriterApp(QObject):
        def __init__(self, preloaded_model=None):
            """
            Initialize the application, opening settings window if no configuration file is found.
            """
            super().__init__()
            self.preloaded_model = preloaded_model
            self.app = QApplication(sys.argv)
            self.app.setWindowIcon(QIcon(os.path.join('assets', 'ww-logo.png')))

            ConfigManager.initialize()

            self.settings_window = SettingsWindow()
            self.settings_window.settings_closed.connect(self.on_settings_closed)
            self.settings_window.settings_saved.connect(self.restart_app)

            if ConfigManager.config_file_exists():
                self.initialize_components()
            else:
                print('No valid configuration file found. Opening settings window...')
                self.settings_window.show()

        def initialize_components(self):
            """
            Initialize the components of the application.
            """
            self.input_simulator = InputSimulator()

            self.key_listener = KeyListener()
            self.key_listener.add_callback("on_activate", self.on_activation)
            self.key_listener.add_callback("on_deactivate", self.on_deactivation)

            model_options = ConfigManager.get_config_section('model_options')
            if self.preloaded_model:
                self.local_model = self.preloaded_model
            else:
                self.local_model = create_local_model() if not model_options.get('use_api') else None

            self.result_thread = None

            self.main_window = MainWindow()
            self.main_window.openSettings.connect(self.settings_window.show)
            self.main_window.startListening.connect(self.key_listener.start)
            self.main_window.closeApp.connect(self.exit_app)

            if not ConfigManager.get_config_value('misc', 'hide_status_window'):
                self.status_window = StatusWindow()

            self.create_tray_icon()
            self.main_window.show()

        def create_tray_icon(self):
            """
            Create the system tray icon and its context menu.
            """
            self.tray_icon = QSystemTrayIcon(QIcon(os.path.join('assets', 'ww-logo.png')), self.app)

            tray_menu = QMenu()

            show_action = QAction('WhisperWriter Main Menu', self.app)
            show_action.triggered.connect(self.main_window.show)
            tray_menu.addAction(show_action)

            settings_action = QAction('Open Settings', self.app)
            settings_action.triggered.connect(self.settings_window.show)
            tray_menu.addAction(settings_action)

            exit_action = QAction('Exit', self.app)
            exit_action.triggered.connect(self.exit_app)
            tray_menu.addAction(exit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

        def cleanup(self):
            if self.key_listener:
                self.key_listener.stop()
            if self.input_simulator:
                self.input_simulator.cleanup()

        def exit_app(self):
            """
            Exit the application.
            """
            self.cleanup()
            QApplication.quit()

        def restart_app(self):
            """Restart the application to apply the new settings."""
            self.cleanup()
            QApplication.quit()
            QProcess.startDetached(sys.executable, sys.argv)

        def on_settings_closed(self):
            """
            If settings is closed without saving on first run, initialize the components with default values.
            """
            if not os.path.exists(os.path.join('src', 'config.yaml')):
                QMessageBox.information(
                    self.settings_window,
                    'Using Default Values',
                    'Settings closed without saving. Default values are being used.'
                )
                self.initialize_components()

        def on_activation(self):
            """
            Called when the activation key combination is pressed.
            """
            if self.result_thread and self.result_thread.isRunning():
                recording_mode = ConfigManager.get_config_value('recording_options', 'recording_mode')
                if recording_mode == 'press_to_toggle':
                    self.result_thread.stop_recording()
                elif recording_mode == 'continuous':
                    self.stop_result_thread()
                return

            self.start_result_thread()

        def on_deactivation(self):
            """
            Called when the activation key combination is released.
            """
            if ConfigManager.get_config_value('recording_options', 'recording_mode') == 'hold_to_record':
                if self.result_thread and self.result_thread.isRunning():
                    self.result_thread.stop_recording()

        def start_result_thread(self):
            """
            Start the result thread to record audio and transcribe it.
            """
            if self.result_thread and self.result_thread.isRunning():
                return

            # Clean up previous thread to prevent QThread/signal accumulation
            self._cleanup_result_thread()

            self.result_thread = ResultThread(self.local_model)
            if not ConfigManager.get_config_value('misc', 'hide_status_window'):
                self.result_thread.statusSignal.connect(self.status_window.updateStatus)
                self.status_window.closeSignal.connect(self.stop_result_thread)
            self.result_thread.resultSignal.connect(self.on_transcription_complete)
            self.result_thread.start()

        def stop_result_thread(self):
            """
            Stop the result thread.
            """
            if self.result_thread and self.result_thread.isRunning():
                self.result_thread.stop()

        def _cleanup_result_thread(self):
            """
            Disconnect signals and schedule deletion of the previous ResultThread
            to prevent QThread accumulation and signal stacking over long sessions.
            """
            if self.result_thread is None:
                return

            # Disconnect all signals from the old thread
            try:
                self.result_thread.statusSignal.disconnect()
            except TypeError:
                pass
            try:
                self.result_thread.resultSignal.disconnect()
            except TypeError:
                pass

            # Disconnect status_window.closeSignal from stop_result_thread
            # (it gets reconnected each cycle otherwise)
            if not ConfigManager.get_config_value('misc', 'hide_status_window'):
                try:
                    self.status_window.closeSignal.disconnect(self.stop_result_thread)
                except TypeError:
                    pass

            # Schedule the old thread for deletion by Qt's event loop
            self.result_thread.deleteLater()
            self.result_thread = None

        def on_transcription_complete(self, result):
            """
            When the transcription is complete, type the result and start listening for the activation key again.
            """
            self.input_simulator.typewrite(result)

            if ConfigManager.get_config_value('misc', 'noise_on_completion'):
                AudioPlayer(os.path.join('assets', 'beep.wav')).play(block=True)

            if ConfigManager.get_config_value('recording_options', 'recording_mode') == 'continuous':
                self.start_result_thread()
            else:
                self.key_listener.start()

        def run(self):
            """
            Start the application.
            """
            sys.exit(self.app.exec_())

    app = WhisperWriterApp(preloaded_model=preloaded_model)
    app.run()


if __name__ == '__main__':
    model = _preload_model()
    _run_app(preloaded_model=model)

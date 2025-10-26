import sys
import os
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QPushButton, 
                             QDialog, QProgressBar, QMessageBox, QScrollArea,
                             QFrame, QListWidgetItem, QTextEdit, QComboBox,
                             QToolBar, QAction, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QColor
from pathlib import Path
import urllib.parse

class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    check_failed = pyqtSignal(str)

    def __init__(self, update_url):
        super().__init__()
        self.update_url = update_url

    def run(self):
        try:
            response = requests.get(self.update_url, timeout=5)
            response.raise_for_status()
            update_data = response.json()
            
            current_version = "1.5.0"
            new_version = update_data.get('version')
            
            if new_version != current_version:
                self.update_available.emit(update_data)
            else:
                self.no_update.emit()
                
        except Exception as e:
            self.check_failed.emit(str(e))

class DataLoader(QThread):
    data_loaded = pyqtSignal(list)
    load_failed = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)

    def __init__(self, data_url):
        super().__init__()
        self.data_url = data_url

    def run(self):
        try:
            self.progress_updated.emit(0, "Загрузка данных...")
            response = requests.get(self.data_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.progress_updated.emit(50, "Обработка данных...")
            programs_data = self.parse_programs_data(data)
            
            self.progress_updated.emit(100, "Загрузка завершена")
            self.data_loaded.emit(programs_data)
            
        except Exception as e:
            self.load_failed.emit(str(e))

    def parse_programs_data(self, data):
        programs_data = []
        
        if isinstance(data, list):
            programs_data = data
        elif isinstance(data, dict):
            if 'programs' in data:
                programs_data = data['programs']
            elif 'applications' in data:
                programs_data = data['applications']
            else:
                for key, value in data.items():
                    if isinstance(value, list):
                        programs_data = value
                        break
        
        validated_data = []
        for program in programs_data:
            if isinstance(program, dict) and program.get('name') and program.get('download_url'):
                validated_data.append(program)
        
        return validated_data

class FileSizeChecker(QThread):
    size_checked = pyqtSignal(str, str)
    check_failed = pyqtSignal(str, str)

    def __init__(self, app_name, download_url):
        super().__init__()
        self.app_name = app_name
        self.download_url = download_url

    def run(self):
        try:
            response = requests.head(self.download_url, timeout=5, allow_redirects=True)
            file_size = int(response.headers.get('content-length', 0))
            
            if file_size > 0:
                size_str = self.format_file_size(file_size)
                self.size_checked.emit(self.app_name, size_str)
            else:
                self.size_checked.emit(self.app_name, "Неизвестно")
                
        except Exception as e:
            self.check_failed.emit(self.app_name, str(e))

    def format_file_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

class DownloadThread(QThread):
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            downloaded = 0
            with open(self.save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.download_finished.emit(self.save_path)
        except Exception as e:
            self.download_error.emit(str(e))

class ThemeManager:
    @staticmethod
    def apply_light_theme(app):
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        app.setPalette(palette)

    @staticmethod
    def apply_dark_theme(app):
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(65, 65, 65))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        app.setPalette(palette)

class UpdateDialog(QDialog):
    def __init__(self, update_data, parent=None):
        super().__init__(parent)
        self.update_data = update_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Новая версия")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Вышло обновление Pidorlauncher")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Новая версия:"))
        version_label = QLabel(self.update_data.get('version', 'Unknown'))
        version_label.setFont(QFont("Arial", 12, QFont.Bold))
        version_layout.addWidget(version_label)
        version_layout.addStretch()
        layout.addLayout(version_layout)
        
        changelog_label = QLabel("Изменения:")
        changelog_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(changelog_label)
        
        changelog_text = QTextEdit()
        changelog_text.setPlainText(self.update_data.get('changelog', 'Нет информации об изменениях'))
        changelog_text.setReadOnly(True)
        changelog_text.setMaximumHeight(150)
        layout.addWidget(changelog_text)
        
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Скачать")
        download_btn.setFixedSize(150, 40)
        download_btn.clicked.connect(self.download_update)
        
        later_btn = QPushButton("Не")
        later_btn.setFixedSize(120, 40)
        later_btn.clicked.connect(self.reject)
        
        ignore_btn = QPushButton("Выключи его нахуй")
        ignore_btn.setFixedSize(120, 40)
        ignore_btn.clicked.connect(self.ignore_update)
        
        button_layout.addStretch()
        button_layout.addWidget(download_btn)
        button_layout.addWidget(later_btn)
        button_layout.addWidget(ignore_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def download_update(self):
        import webbrowser
        download_url = self.update_data.get('download_url', '')
        if download_url:
            webbrowser.open(download_url)
        self.accept()
    
    def ignore_update(self):
        self.accept()

class AppDetailsDialog(QDialog):
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"{self.app_data['name']} - Подробнее")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(96, 96)
        self.icon_label.setStyleSheet("border: 2px solid #555; border-radius: 8px; padding: 5px; background: #333;")
        header_layout.addWidget(self.icon_label)
        
        info_layout = QVBoxLayout()
        self.title_label = QLabel(self.app_data['name'])
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        version_text = f"Версия: {self.app_data.get('version', 'Не указана')}"
        developer = self.app_data.get('developer')
        if developer:
            version_text += f" | Разработчик: {developer}"
        
        self.version_label = QLabel(version_text)
        self.version_label.setFont(QFont("Arial", 12))
        
        self.size_label = QLabel("Размер: загрузка...")
        self.size_label.setFont(QFont("Arial", 10))
        self.size_label.setStyleSheet("color: #666;")
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.version_label)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        desc_label = QLabel("Описание:")
        desc_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(desc_label)
        
        description = QTextEdit()
        description.setPlainText(self.app_data.get('description', 'Описание отсутствует'))
        description.setReadOnly(True)
        description.setMaximumHeight(100)
        description.setStyleSheet("background: #2d2d2d; border: 1px solid #555; border-radius: 5px; padding: 8px; color: white;")
        layout.addWidget(description)
        
        screenshots_label = QLabel("Скриншоты:")
        screenshots_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(screenshots_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.screenshots_layout = QHBoxLayout()
        self.screenshots_layout.setSpacing(10)
        self.scroll_widget.setLayout(self.screenshots_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setMinimumHeight(250)
        self.scroll_area.setStyleSheet("background: #2d2d2d; border: 1px solid #555; border-radius: 5px;")
        layout.addWidget(self.scroll_area)
        
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Скачать")
        download_btn.setFixedSize(180, 45)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ccc;
            }
        """)
        download_btn.clicked.connect(self.start_download)
        
        if not self.app_data.get('download_url'):
            download_btn.setEnabled(False)
            download_btn.setToolTip("Ссылка для скачивания недоступна")
        
        close_btn = QPushButton("✕ Закрыть")
        close_btn.setFixedSize(120, 45)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(download_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        QTimer.singleShot(100, self.load_app_data)
    
    def load_app_data(self):
        icon_url = self.app_data.get('icon_url')
        if icon_url:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(icon_url, timeout=5).content)
                if not pixmap.isNull():
                    self.icon_label.setPixmap(pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                self.icon_label.setText("❌\nИконка")
        else:
            self.icon_label.setText("📁\nНет иконки")
        
        download_url = self.app_data.get('download_url')
        if download_url:
            self.size_checker = FileSizeChecker(self.app_data['name'], download_url)
            self.size_checker.size_checked.connect(self.on_size_checked)
            self.size_checker.check_failed.connect(self.on_size_check_failed)
            self.size_checker.start()
        
        screenshots = self.app_data.get('screenshots', [])
        for i, screenshot_url in enumerate(screenshots):
            QTimer.singleShot(i * 200, lambda url=screenshot_url: self.load_screenshot(url))
    
    def on_size_checked(self, app_name, size_str):
        if app_name == self.app_data['name']:
            self.size_label.setText(f"Размер: {size_str}")
    
    def on_size_check_failed(self, app_name, error_msg):
        if app_name == self.app_data['name']:
            self.size_label.setText("Размер: неизвестно")
    
    def load_screenshot(self, screenshot_url):
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(screenshot_url, timeout=5).content)
            if not pixmap.isNull():
                screenshot_label = QLabel()
                screenshot_label.setPixmap(pixmap.scaled(400, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                screenshot_label.setStyleSheet("border: 2px solid #555; border-radius: 5px; padding: 3px; background: #333;")
                screenshot_label.setFixedSize(400, 250)
                self.screenshots_layout.addWidget(screenshot_label)
        except Exception as e:
            print(f"Ошибка загрузки скриншота: {e}")
    
    def start_download(self):
        if self.app_data.get('download_url'):
            self.parent().show_download_progress(self.app_data)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Ссылка для скачивания недоступна")

class DownloadProgressDialog(QDialog):
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.download_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Скачивание")
        self.setFixedSize(450, 180)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(f"Скачивание: {self.app_data['name']}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Получение данных...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11px; color: #ccc;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        QTimer.singleShot(500, self.start_download)
    
    def start_download(self):
        try:
            downloads_dir = Path.home() / "Downloads"
            downloads_dir.mkdir(exist_ok=True)
            
            download_url = self.app_data.get('download_url', '')
            if download_url:
                filename = os.path.basename(urllib.parse.urlparse(download_url).path)
                if not filename:
                    filename = f"{self.app_data['name'].replace(' ', '_')}.exe"
            else:
                filename = f"{self.app_data['name'].replace(' ', '_')}.exe"
                
            save_path = downloads_dir / filename
            
            self.download_thread = DownloadThread(download_url, str(save_path))
            self.download_thread.progress_updated.connect(self.update_progress)
            self.download_thread.download_finished.connect(self.download_complete)
            self.download_thread.download_error.connect(self.download_error)
            self.download_thread.start()
            
        except Exception as e:
            self.download_error(str(e))
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Прогресс: {value}%")
    
    def download_complete(self, file_path):
        self.progress_bar.setValue(100)
        self.status_label.setText("Готово!")
        QTimer.singleShot(1000, self.show_completion_message)
    
    def show_completion_message(self):
        msg = QMessageBox()
        msg.setWindowTitle("Скачанно")
        msg.setText("Программа загруженна.")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        self.accept()
    
    def download_error(self, error_msg):
        self.status_label.setText("❌ Ошибка скачивания!")
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setText(f"Ошибка при скачивании: {error_msg}")
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()
        self.reject()

class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, app_data):
        super().__init__()
        self.app_data = app_data
        text = f"{app_data['name']}\nВерсия: {app_data.get('version', 'Не указана')}"
        developer = app_data.get('developer')
        if developer:
            text += f" | {developer}"
        self.setText(text)

class SoftwareDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.update_url = "https://zenusus.serv00.net/updates/version.json"
        self.programs_data_url = "https://zenusus.serv00.net/programs/programs.json"
        
        self.apps_data = []
        self.current_theme = "light"
        self.init_ui()
        
        QTimer.singleShot(100, self.start_initial_loading)
    
    def start_initial_loading(self):
        self.check_for_updates()
    
    def check_for_updates(self):
        self.statusBar().showMessage("Проверка обновлений...")
        self.loading_progress.setValue(25)
        
        self.update_checker = UpdateChecker(self.update_url)
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.check_failed.connect(self.on_update_check_failed)
        self.update_checker.start()
    
    def load_programs_data(self):
        self.statusBar().showMessage("Загрузка данных о программах...")
        self.loading_progress.setValue(50)
        
        self.data_loader = DataLoader(self.programs_data_url)
        self.data_loader.data_loaded.connect(self.on_data_loaded)
        self.data_loader.load_failed.connect(self.on_data_load_failed)
        self.data_loader.progress_updated.connect(self.on_data_progress_updated)
        self.data_loader.start()
    
    def on_data_progress_updated(self, progress, message):
        self.loading_progress.setValue(50 + progress // 2)
        self.status_label.setText(message)
    
    def init_ui(self):
        self.setWindowTitle("Pidorlauncher")
        self.setMinimumSize(900, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.create_toolbar()
        self.setStatusBar(QStatusBar())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("Доступно для загрузки:")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title_label)
        
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)
        self.loading_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
        """)
        layout.addWidget(self.loading_progress)
        
        self.status_label = QLabel("Минутку...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 8px;")
        layout.addWidget(self.status_label)
        
        self.apps_list = QListWidget()
        self.apps_list.itemDoubleClicked.connect(self.on_app_double_clicked)
        self.apps_list.setIconSize(QSize(48, 48))
        self.apps_list.setSpacing(8)
        self.update_list_style()
        layout.addWidget(self.apps_list)
        
        control_layout = QHBoxLayout()
        
        self.reload_btn = QPushButton("🔄 Обновить данные")
        self.reload_btn.setFixedSize(150, 35)
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        self.reload_btn.clicked.connect(self.reload_data)
        self.reload_btn.setEnabled(False)
        
        control_layout.addWidget(self.reload_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        central_widget.setLayout(layout)
    
    def update_list_style(self):
        if self.current_theme == "dark":
            self.apps_list.setStyleSheet("""
                QListWidget {
                    background: #2d2d2d;
                    border: 2px solid #555;
                    border-radius: 8px;
                    padding: 5px;
                    font-size: 12px;
                    color: white;
                }
                QListWidget::item {
                    background: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 2px;
                    color: white;
                }
                QListWidget::item:selected {
                    background: #4a4a4a;
                    border: 2px solid #2196f3;
                }
                QListWidget::item:hover {
                    background: #4a4a4a;
                    border: 1px solid #666;
                }
            """)
        else:
            self.apps_list.setStyleSheet("""
                QListWidget {
                    background: white;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 5px;
                    font-size: 12px;
                }
                QListWidget::item {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 2px;
                }
                QListWidget::item:selected {
                    background: #e3f2fd;
                    border: 2px solid #2196f3;
                }
                QListWidget::item:hover {
                    background: #e9ecef;
                    border: 1px solid #adb5bd;
                }
            """)
    
    def create_toolbar(self):
        toolbar = QToolBar("Панель параметров")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        theme_label = QLabel("Тема:")
        toolbar.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_combo)
        
        toolbar.addSeparator()
        
        refresh_action = QAction("🔄 Обновить", self)
        refresh_action.triggered.connect(self.reload_data)
        toolbar.addAction(refresh_action)
    
    def change_theme(self, theme_name):
        app = QApplication.instance()
        if theme_name == "Темная":
            ThemeManager.apply_dark_theme(app)
            self.current_theme = "dark"
        else:
            ThemeManager.apply_light_theme(app)
            self.current_theme = "light"
        self.update_list_style()
    
    def on_data_loaded(self, programs_data):
        try:
            if not programs_data:
                self.show_error("Нет данных о программах для отображения")
                return
                
            self.apps_data = programs_data
            self.status_label.setText(f"Полученно {len(programs_data)} приложений\n Созданно GovNo corp. Версия: 1.5R")
            self.loading_progress.setValue(100)
            self.statusBar().showMessage(f"Загружено {len(programs_data)} приложений", 3000)
            
            self.apps_list.clear()
            for app in programs_data:
                item = CustomListWidgetItem(app)
                self.apps_list.addItem(item)
            
            self.load_icons_async()
            self.reload_btn.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"Ошибка обработки данных: {str(e)}")
    
    def load_icons_async(self):
        for i in range(self.apps_list.count()):
            QTimer.singleShot(i * 100, lambda idx=i: self.load_icon_for_item(idx))
    
    def load_icon_for_item(self, index):
        item = self.apps_list.item(index)
        app_data = item.app_data
        icon_url = app_data.get('icon_url')
        
        if icon_url:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(icon_url, timeout=5).content)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    item.setIcon(icon)
            except Exception as e:
                print(f"Ошибка загрузки иконки для {app_data['name']}: {e}")
    
    def on_data_load_failed(self, error_msg):
        self.show_error(f"Не удалось загрузить данные: {error_msg}")
        self.status_label.setText("❌ Ошибка загрузки данных")
        self.loading_progress.setValue(0)
        self.statusBar().showMessage("Ошибка загрузки данных", 5000)
        self.reload_btn.setEnabled(True)
    
    def show_update_dialog(self, update_data):
        QTimer.singleShot(100, lambda: self._show_update_dialog(update_data))
    
    def _show_update_dialog(self, update_data):
        dialog = UpdateDialog(update_data, self)
        dialog.finished.connect(self.on_update_dialog_closed)
        dialog.show()
    
    def on_update_dialog_closed(self):
        QTimer.singleShot(100, self.load_programs_data)
    
    def on_no_update(self):
        self.statusBar().showMessage("Приложение обновлено", 2000)
        self.load_programs_data()
    
    def on_update_check_failed(self, error_msg):
        print(f"Ошибка проверки обновлений: {error_msg}")
        self.statusBar().showMessage("Не удалось проверить обновления", 3000)
        self.load_programs_data()
    
    def reload_data(self):
        self.apps_list.clear()
        self.status_label.setText("Обновление данных...")
        self.loading_progress.setValue(0)
        self.reload_btn.setEnabled(False)
        self.check_for_updates()
    
    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
    
    def on_app_double_clicked(self, item):
        self.current_app_data = item.app_data
        
        if not self.current_app_data.get('name'):
            self.show_error("У приложения отсутствует название")
            return
        
        if not self.current_app_data.get('download_url'):
            self.show_error("У приложения отсутствует ссылка для скачивания")
            return
            
        self.show_app_details()
    
    def show_app_details(self):
        if hasattr(self, 'current_app_data'):
            dialog = AppDetailsDialog(self.current_app_data, self)
            dialog.exec_()
    
    def show_download_progress(self, app_data):
        dialog = DownloadProgressDialog(app_data, self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    ThemeManager.apply_light_theme(app)
    
    window = SoftwareDownloaderApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
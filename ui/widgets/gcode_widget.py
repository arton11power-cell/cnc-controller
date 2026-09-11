"""G-code editor and management widget"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QLabel, QProgressBar,
    QSpinBox, QComboBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer


class GCodeWidget(QWidget):
    """Widget for G-code editing and execution"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize G-code widget UI"""
        main_layout = QVBoxLayout()

        # File operations
        file_group = QGroupBox("Файл G-кода")
        file_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Открыть")
        open_btn.clicked.connect(self.open_gcode_file)
        file_layout.addWidget(open_btn)

        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_gcode_file)
        file_layout.addWidget(save_btn)

        clear_btn = QPushButton("🗑️ Очистить")
        clear_btn.clicked.connect(self.clear_gcode)
        file_layout.addWidget(clear_btn)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # G-code text editor
        editor_group = QGroupBox("Редактор G-кода")
        editor_layout = QVBoxLayout()

        self.gcode_editor = QTextEdit()
        self.gcode_editor.setPlaceholderText(
            "Введите G-код здесь...\n\n"
            "Примеры:\n"
            "G0 X10 Y10 Z5    ; Быстрое движение\n"
            "G1 X20 Z0 F100   ; Линейное движение со скоростью 100\n"
            "M3 S1000          ; Включить шпиндель на 1000 об/мин\n"
            "M5                ; Отключить шпиндель"
        )
        editor_layout.addWidget(self.gcode_editor)

        editor_group.setLayout(editor_layout)
        main_layout.addWidget(editor_group)

        # Program control
        control_group = QGroupBox("Управление программой")
        control_layout = QGridLayout()

        send_btn = QPushButton("📤 Отправить в станок")
        send_btn.setStyleSheet("background-color: #2196F3; color: white;")
        send_btn.clicked.connect(self.send_gcode_to_machine)
        control_layout.addWidget(send_btn, 0, 0)

        start_btn = QPushButton("▶️ Запустить")
        start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        start_btn.clicked.connect(self.start_program)
        control_layout.addWidget(start_btn, 0, 1)

        pause_btn = QPushButton("⏸️ Пауза")
        pause_btn.setStyleSheet("background-color: #FF9800; color: white;")
        pause_btn.clicked.connect(self.pause_program)
        control_layout.addWidget(pause_btn, 0, 2)

        stop_btn = QPushButton("⏹️ Стоп")
        stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        stop_btn.clicked.connect(self.stop_program)
        control_layout.addWidget(stop_btn, 0, 3)

        # Progress display
        control_layout.addWidget(QLabel("Прогресс:"), 1, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        control_layout.addWidget(self.progress_bar, 1, 1, 1, 3)

        # Line counter
        control_layout.addWidget(QLabel("Текущая строка:"), 2, 0)
        self.line_counter = QLabel("0 / 0")
        control_layout.addWidget(self.line_counter, 2, 1)

        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def open_gcode_file(self):
        """Open G-code file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть G-код",
            "",
            "G-code Files (*.gcode *.nc *.gcode);;Text Files (*.txt);;All Files (*.*)"
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.gcode_editor.setText(f.read())
                QMessageBox.information(self, "Успех", f"Файл загружен: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_gcode_file(self):
        """Save G-code file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить G-код",
            "",
            "G-code Files (*.gcode);;NC Files (*.nc);;Text Files (*.txt)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.gcode_editor.toPlainText())
                QMessageBox.information(self, "Успех", f"Файл сохранен: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def clear_gcode(self):
        """Clear G-code editor"""
        reply = QMessageBox.question(
            self,
            "Очистить",
            "Вы уверены, что хотите очистить редактор?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.gcode_editor.clear()

    def send_gcode_to_machine(self):
        """Send G-code to machine"""
        gcode = self.gcode_editor.toPlainText()
        
        if not gcode.strip():
            QMessageBox.warning(self, "Ошибка", "G-код не введен!")
            return

        if not self.controller.is_connected():
            QMessageBox.warning(self, "Ошибка", "Станок не подключен!")
            return

        try:
            lines = gcode.strip().split('\n')
            self.controller.load_gcode_program(lines)
            QMessageBox.information(
                self,
                "Успех",
                f"Программа загружена: {len(lines)} строк G-кода"
            )
            self.line_counter.setText(f"0 / {len(lines)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")

    def start_program(self):
        """Start G-code program"""
        if not self.controller.is_connected():
            QMessageBox.warning(self, "Ошибка", "Станок не подключен!")
            return

        try:
            self.controller.start_program()
            QMessageBox.information(self, "Успех", "Программа запущена")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def pause_program(self):
        """Pause G-code program"""
        try:
            self.controller.pause_program()
            QMessageBox.information(self, "Пауза", "Программа приостановлена")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def stop_program(self):
        """Stop G-code program"""
        try:
            self.controller.stop_program()
            QMessageBox.information(self, "Остановка", "Программа остановлена")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

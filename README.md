# CNC Controller

Десктопное приложение для управления станком с ЧПУ (числовым программным управлением).

## Возможности

- 📊 Управление осями (X, Y, Z)
- 📈 Обработка G-кода
- 🔧 Контроль параметров станка
- 💾 Сохранение и загрузка программ
- 📡 Взаимодействие с контроллером через последовательный порт/Ethernet
- 📉 Мониторинг состояния в реальном времени

## Требования

- Python 3.8+
- PyQt5
- pyserial (для работы с последовательным портом)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/arton11power-cell/cnc-controller.git
cd cnc-controller
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Структура проекта

```
cnc-controller/
├── main.py                 # Точка входа приложения
├── requirements.txt        # Зависимости проекта
├── ui/                     # Интерфейс пользователя
│   ├── main_window.py
│   ├── widgets/
│   └── dialogs/
├── core/                   # Основная логика
│   ├── controller.py       # Логика контроллера
│   ├── gcode_parser.py     # Парсер G-кода
│   └── serial_handler.py   # Работа с портами
├── models/                 # Модели данных
│   └── machine_state.py
└── utils/                  # Вспомогательные функции
    └── config.py
```

## Лицензия

MIT

## Автор

arton11power-cell

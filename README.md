# FPGA Design for Intel Cyclone IV EP4CE6E22 - CNC Controller

## Описание

VHDL дизайн для FPGA, обеспечивающий высокоскоростную генерацию импульсов для 5-осевого станка с ЧПУ.

## Основные функции

- ⚡ Генерация высокоскоростных импульсов для шаговых двигателей (до 1 МГц)
- 🔄 Синхронизация движения 5 осей (X, Y, Z, A, B)
- 📊 Обработка сигналов датчиков в реальном времени
- 🎛️ PWM управление шпинделем и охлаждением
- 📡 UART интерфейс с STM32H743VIT6
- 💾 Встроенная буферизация команд
- 🛡️ Система обнаружения ошибок

## Параметры

- **Тактовая частота**: 50 МГц (встроенный осциллятор Cyclone IV)
- **Максимальная частота импульсов**: 1 МГц на ось
- **Разрешение по положению**: 32-бит
- **Интерфейс связи**: UART 921600 baud
- **Память**: 1008 ЛЭ, 23 Кбит SRAM

## Структура проекта

```
fpga/cyclone-iv/
├── README.md
├── rtl/
│   ├── top.vhd                    # Верхний уровень дизайна
│   ├── pulse_generator.vhd        # Генератор импульсов
│   ├── axis_controller.vhd        # Контроллер оси
│   ├── uart_interface.vhd         # UART интерфейс
│   ├── command_decoder.vhd        # Декодер команд
│   ├── pwm_controller.vhd         # PWM контроллер
│   ├── synchronizer.vhd           # Синхронизатор осей
│   └── status_monitor.vhd         # Монитор состояния
├── sim/
│   ├── tb_top.vhd                 # Тестбенч верхнего уровня
│   ├── tb_pulse_generator.vhd     # Тестбенч генератора
│   └── tb_uart_interface.vhd      # Тестбенч UART
├── constraints/
│   └── ep4ce6.qsf                 # Quartos Settings File
├── Makefile
└── .gitignore
```

## Пиновое назначение (EP4CE6E22)

### Входы/Выходы для двигателей (LVTTL)
- A0 (X-axis pulse), A1 (X-axis direction)
- A2 (Y-axis pulse), A3 (Y-axis direction)
- A4 (Z-axis pulse), A5 (Z-axis direction)
- A6 (A-axis pulse), A7 (A-axis direction)
- A8 (B-axis pulse), A9 (B-axis direction)

### Входы датчиков (LVTTL)
- B0 (X-endstop), B1 (Y-endstop)
- B2 (Z-endstop), B3 (A-endstop)
- B4 (B-endstop)

### Коммуникация
- UART RX: Pin 25
- UART TX: Pin 26

### Питание
- 3.3V VCC, GND

## Инструменты разработки

- Intel Quartus Prime Lite
- ModelSim (для симуляции)
- GHDL (опционально)

## Сборка

```bash
# Через Quartus (GUI)
quartus -t build.tcl

# Или через Makefile
make
make sim      # Запуск симуляции
make program  # Программирование FPGA
make clean
```

## Протокол коммуникации (UART)

### Формат команды
```
[SYNC] [CMD] [LEN_L] [LEN_H] [DATA...]
 0xAA    0x??   0x??    0x??  [до 256 байт]
```

### Команды
- **0x01**: SYNC - синхронизация осей
- **0x02**: PULSE - отправить импульсы
- **0x03**: STATUS - запрос статуса
- **0x04**: RESET - сброс контроллера
- **0x05**: PWM - управление PWM

## Лицензия

MIT

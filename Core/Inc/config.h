#ifndef __CONFIG_H
#define __CONFIG_H

/* CNC Controller Configuration - 5-Axis Machine */

/* Motor Control - 5 Axes (X, Y, Z, A, B) */
#define MOTOR_X_STEP_PIN    GPIO_PIN_0
#define MOTOR_X_DIR_PIN     GPIO_PIN_1
#define MOTOR_Y_STEP_PIN    GPIO_PIN_2
#define MOTOR_Y_DIR_PIN     GPIO_PIN_3
#define MOTOR_Z_STEP_PIN    GPIO_PIN_4
#define MOTOR_Z_DIR_PIN     GPIO_PIN_5
#define MOTOR_A_STEP_PIN    GPIO_PIN_8
#define MOTOR_A_DIR_PIN     GPIO_PIN_9
#define MOTOR_B_STEP_PIN    GPIO_PIN_10
#define MOTOR_B_DIR_PIN     GPIO_PIN_11
#define MOTOR_ENABLE_PIN    GPIO_PIN_6
#define MOTOR_PORT          GPIOA

/* Sensor Configuration */
#define SENSOR_X_ENDSTOP_PIN    GPIO_PIN_0
#define SENSOR_Y_ENDSTOP_PIN    GPIO_PIN_1
#define SENSOR_Z_ENDSTOP_PIN    GPIO_PIN_2
#define SENSOR_A_ENDSTOP_PIN    GPIO_PIN_3
#define SENSOR_B_ENDSTOP_PIN    GPIO_PIN_4
#define SENSOR_PORT             GPIOB

/* UART Configuration */
#define UART_PC_BAUDRATE   115200
#define UART_FPGA_BAUDRATE 921600

/* Motor Parameters */
#define MOTOR_STEPS_PER_MM  800  /* Шаги на миллиметр */
#define MOTOR_MAX_SPEED     5000 /* Максимальная частота (Hz) */
#define MOTOR_ACCELERATION  100  /* Ускорение (mm/s^2) */

/* Spindle Control */
#define SPINDLE_PWM_FREQ    20000 /* 20 kHz */
#define SPINDLE_MIN_SPEED   1000
#define SPINDLE_MAX_SPEED   24000

/* G-code Memory Storage */
#define GCODE_MEMORY_START      0x60000000  /* Internal RAM start address */
#define GCODE_MEMORY_SIZE       (512 * 1024) /* 512 KB for G-code storage */
#define GCODE_MAX_LINES         2000
#define GCODE_LINE_MAX_LENGTH   128

#endif /* __CONFIG_H */

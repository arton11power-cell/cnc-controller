#ifndef __SENSOR_H
#define __SENSOR_H

#include "stm32h7xx_hal.h"
#include <stdint.h>

/* Sensor types - 5 Axes */
typedef enum {
    SENSOR_X_ENDSTOP = 0,
    SENSOR_Y_ENDSTOP = 1,
    SENSOR_Z_ENDSTOP = 2,
    SENSOR_A_ENDSTOP = 3,
    SENSOR_B_ENDSTOP = 4,
    SENSOR_COUNT = 5
} SensorType;

/* Sensor state */
typedef struct {
    uint8_t triggered;
    uint32_t trigger_time;
} SensorState;

/* Function prototypes */
void sensor_init(void);
SensorState* sensor_get_state(SensorType sensor);
uint8_t sensor_is_triggered(SensorType sensor);
void sensor_update(void);

#endif /* __SENSOR_H */

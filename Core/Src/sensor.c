#include "sensor.h"

static SensorState sensor_states[SENSOR_COUNT] = {0};

/**
 * Initialize sensors for 5 axes
 */
void sensor_init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* Enable GPIOB clock */
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    /* Configure sensor pins as inputs */
    GPIO_InitStruct.Pin = SENSOR_X_ENDSTOP_PIN | SENSOR_Y_ENDSTOP_PIN | 
                         SENSOR_Z_ENDSTOP_PIN | SENSOR_A_ENDSTOP_PIN | 
                         SENSOR_B_ENDSTOP_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    
    HAL_GPIO_Init(SENSOR_PORT, &GPIO_InitStruct);
    
    /* Initialize sensor states */
    for (int i = 0; i < SENSOR_COUNT; i++) {
        sensor_states[i].triggered = 0;
        sensor_states[i].trigger_time = 0;
    }
}

/**
 * Get sensor state
 */
SensorState* sensor_get_state(SensorType sensor)
{
    if (sensor >= SENSOR_COUNT) return NULL;
    return &sensor_states[sensor];
}

/**
 * Check if sensor is triggered
 */
uint8_t sensor_is_triggered(SensorType sensor)
{
    if (sensor >= SENSOR_COUNT) return 0;
    return sensor_states[sensor].triggered;
}

/**
 * Update sensor states (call periodically)
 */
void sensor_update(void)
{
    GPIO_PinState state_x = HAL_GPIO_ReadPin(SENSOR_PORT, SENSOR_X_ENDSTOP_PIN);
    GPIO_PinState state_y = HAL_GPIO_ReadPin(SENSOR_PORT, SENSOR_Y_ENDSTOP_PIN);
    GPIO_PinState state_z = HAL_GPIO_ReadPin(SENSOR_PORT, SENSOR_Z_ENDSTOP_PIN);
    GPIO_PinState state_a = HAL_GPIO_ReadPin(SENSOR_PORT, SENSOR_A_ENDSTOP_PIN);
    GPIO_PinState state_b = HAL_GPIO_ReadPin(SENSOR_PORT, SENSOR_B_ENDSTOP_PIN);
    
    sensor_states[SENSOR_X_ENDSTOP].triggered = (state_x == GPIO_PIN_RESET) ? 1 : 0;
    sensor_states[SENSOR_Y_ENDSTOP].triggered = (state_y == GPIO_PIN_RESET) ? 1 : 0;
    sensor_states[SENSOR_Z_ENDSTOP].triggered = (state_z == GPIO_PIN_RESET) ? 1 : 0;
    sensor_states[SENSOR_A_ENDSTOP].triggered = (state_a == GPIO_PIN_RESET) ? 1 : 0;
    sensor_states[SENSOR_B_ENDSTOP].triggered = (state_b == GPIO_PIN_RESET) ? 1 : 0;
}

#include "motor_control.h"

static MotorState motor_states[AXIS_COUNT] = {0};
static uint8_t motor_enabled = 0;

static const char* axis_names[AXIS_COUNT] = {"X", "Y", "Z", "A", "B"};

/**
 * Initialize motor control for 5 axes
 */
void motor_init(void)
{
    /* Initialize GPIO for motor control */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* Enable GPIOA clock */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    /* Configure motor pins as outputs */
    GPIO_InitStruct.Pin = MOTOR_X_STEP_PIN | MOTOR_X_DIR_PIN | 
                         MOTOR_Y_STEP_PIN | MOTOR_Y_DIR_PIN | 
                         MOTOR_Z_STEP_PIN | MOTOR_Z_DIR_PIN | 
                         MOTOR_A_STEP_PIN | MOTOR_A_DIR_PIN |
                         MOTOR_B_STEP_PIN | MOTOR_B_DIR_PIN |
                         MOTOR_ENABLE_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    
    HAL_GPIO_Init(MOTOR_PORT, &GPIO_InitStruct);
    
    /* Initialize motor states */
    for (int i = 0; i < AXIS_COUNT; i++) {
        motor_states[i].position = 0.0f;
        motor_states[i].target_position = 0.0f;
        motor_states[i].speed = 0.0f;
        motor_states[i].acceleration = MOTOR_ACCELERATION;
        motor_states[i].direction = 1;
        motor_states[i].enabled = 0;
    }
    
    motor_enabled = 0;
}

/**
 * Enable all motors
 */
void motor_enable(void)
{
    HAL_GPIO_WritePin(MOTOR_PORT, MOTOR_ENABLE_PIN, GPIO_PIN_RESET);
    motor_enabled = 1;
}

/**
 * Disable all motors
 */
void motor_disable(void)
{
    HAL_GPIO_WritePin(MOTOR_PORT, MOTOR_ENABLE_PIN, GPIO_PIN_SET);
    motor_enabled = 0;
}

/**
 * Move motor to target position
 */
void motor_move(MotorAxis axis, float distance, float speed)
{
    if (axis >= AXIS_COUNT) return;
    
    motor_states[axis].target_position = motor_states[axis].position + distance;
    motor_states[axis].speed = speed;
    motor_states[axis].direction = (distance > 0) ? 1 : -1;
}

/**
 * Set motor speed
 */
void motor_set_speed(MotorAxis axis, float speed)
{
    if (axis >= AXIS_COUNT) return;
    motor_states[axis].speed = speed;
}

/**
 * Stop motor
 */
void motor_stop(MotorAxis axis)
{
    if (axis >= AXIS_COUNT) return;
    motor_states[axis].speed = 0.0f;
    motor_states[axis].target_position = motor_states[axis].position;
}

/**
 * Emergency stop - disable all motors
 */
void motor_emergency_stop(void)
{
    motor_disable();
    for (int i = 0; i < AXIS_COUNT; i++) {
        motor_states[i].speed = 0.0f;
    }
}

/**
 * Get motor state
 */
MotorState* motor_get_state(MotorAxis axis)
{
    if (axis >= AXIS_COUNT) return NULL;
    return &motor_states[axis];
}

/**
 * Get axis name
 */
const char* motor_axis_name(MotorAxis axis)
{
    if (axis >= AXIS_COUNT) return "?";
    return axis_names[axis];
}

/**
 * Update motor positions (call periodically)
 */
void motor_update(void)
{
    if (!motor_enabled) return;
    
    for (int i = 0; i < AXIS_COUNT; i++) {
        MotorState* state = &motor_states[i];
        
        /* Update position based on speed */
        if (state->speed > 0) {
            state->position += (state->speed / 60.0f) * state->direction;
        }
    }
}

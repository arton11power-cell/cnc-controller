#ifndef __MOTOR_CONTROL_H
#define __MOTOR_CONTROL_H

#include "stm32h7xx_hal.h"
#include "config.h"

/* Motor axis enumeration - 5 Axes */
typedef enum {
    AXIS_X = 0,
    AXIS_Y = 1,
    AXIS_Z = 2,
    AXIS_A = 3,  /* Rotation around X axis */
    AXIS_B = 4,  /* Rotation around Y axis */
    AXIS_COUNT = 5
} MotorAxis;

/* Motor state structure */
typedef struct {
    float position;        /* Current position in mm or degrees */
    float target_position; /* Target position */
    float speed;          /* Current speed (mm/min or deg/min) */
    float acceleration;   /* Acceleration */
    int direction;        /* 1 or -1 */
    uint8_t enabled;      /* Motor enabled flag */
} MotorState;

/* Function prototypes */
void motor_init(void);
void motor_enable(void);
void motor_disable(void);
void motor_move(MotorAxis axis, float distance, float speed);
void motor_set_speed(MotorAxis axis, float speed);
void motor_stop(MotorAxis axis);
void motor_emergency_stop(void);
MotorState* motor_get_state(MotorAxis axis);
void motor_update(void);
const char* motor_axis_name(MotorAxis axis);

#endif /* __MOTOR_CONTROL_H */

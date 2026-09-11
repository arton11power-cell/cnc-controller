#ifndef __GCODE_STORAGE_H
#define __GCODE_STORAGE_H

#include "stm32h7xx_hal.h"
#include "config.h"
#include <stdint.h>
#include <string.h>

/* G-code line structure */
typedef struct {
    char command[GCODE_LINE_MAX_LENGTH];
    uint16_t length;
} GCodeLine;

/* G-code program structure */
typedef struct {
    GCodeLine lines[GCODE_MAX_LINES];
    uint16_t line_count;
    uint16_t current_line;
    char program_name[64];
    uint8_t is_running;
} GCodeProgram;

/* Function prototypes */
void gcode_storage_init(void);
void gcode_storage_clear(void);
uint32_t gcode_storage_get_free_space(void);
uint8_t gcode_storage_add_line(const char* line, uint16_t length);
char* gcode_storage_get_line(uint16_t index);
uint16_t gcode_storage_get_line_count(void);
void gcode_storage_start_program(void);
void gcode_storage_stop_program(void);
char* gcode_storage_get_next_line(void);
void gcode_storage_reset_program(void);
uint8_t gcode_storage_is_program_running(void);

#endif /* __GCODE_STORAGE_H */

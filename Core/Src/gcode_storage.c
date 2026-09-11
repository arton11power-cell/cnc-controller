#include "gcode_storage.h"

static GCodeProgram gcode_program = {0};
static uint8_t* gcode_memory_ptr = (uint8_t*)GCODE_MEMORY_START;

/**
 * Initialize G-code storage in STM32 memory
 */
void gcode_storage_init(void)
{
    /* Clear program structure */
    memset(&gcode_program, 0, sizeof(GCodeProgram));
    gcode_memory_ptr = (uint8_t*)GCODE_MEMORY_START;
}

/**
 * Clear all G-code from storage
 */
void gcode_storage_clear(void)
{
    memset(&gcode_program, 0, sizeof(GCodeProgram));
    memset((void*)GCODE_MEMORY_START, 0, GCODE_MEMORY_SIZE);
    gcode_memory_ptr = (uint8_t*)GCODE_MEMORY_START;
}

/**
 * Get free space in G-code storage
 */
uint32_t gcode_storage_get_free_space(void)
{
    uint32_t used = (uint32_t)((uintptr_t)gcode_memory_ptr - GCODE_MEMORY_START);
    return GCODE_MEMORY_SIZE - used;
}

/**
 * Add a G-code line to storage
 */
uint8_t gcode_storage_add_line(const char* line, uint16_t length)
{
    if (gcode_program.line_count >= GCODE_MAX_LINES) {
        return 0; /* Max lines reached */
    }
    
    if (length > GCODE_LINE_MAX_LENGTH) {
        return 0; /* Line too long */
    }
    
    if (gcode_storage_get_free_space() < length + 1) {
        return 0; /* Not enough memory */
    }
    
    /* Copy line to storage */
    GCodeLine* gcode_line = &gcode_program.lines[gcode_program.line_count];
    memcpy(gcode_line->command, line, length);
    gcode_line->command[length] = '\0';
    gcode_line->length = length;
    
    gcode_program.line_count++;
    return 1;
}

/**
 * Get G-code line at index
 */
char* gcode_storage_get_line(uint16_t index)
{
    if (index >= gcode_program.line_count) {
        return NULL;
    }
    
    return gcode_program.lines[index].command;
}

/**
 * Get total number of G-code lines
 */
uint16_t gcode_storage_get_line_count(void)
{
    return gcode_program.line_count;
}

/**
 * Start G-code program execution
 */
void gcode_storage_start_program(void)
{
    gcode_program.current_line = 0;
    gcode_program.is_running = 1;
}

/**
 * Stop G-code program execution
 */
void gcode_storage_stop_program(void)
{
    gcode_program.is_running = 0;
}

/**
 * Get next G-code line for execution
 */
char* gcode_storage_get_next_line(void)
{
    if (!gcode_program.is_running) {
        return NULL;
    }
    
    if (gcode_program.current_line >= gcode_program.line_count) {
        gcode_program.is_running = 0; /* Program finished */
        return NULL;
    }
    
    char* line = gcode_program.lines[gcode_program.current_line].command;
    gcode_program.current_line++;
    
    return line;
}

/**
 * Reset program to start
 */
void gcode_storage_reset_program(void)
{
    gcode_program.current_line = 0;
    gcode_program.is_running = 0;
}

/**
 * Check if program is running
 */
uint8_t gcode_storage_is_program_running(void)
{
    return gcode_program.is_running;
}

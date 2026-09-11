#include "main.h"
#include "gcode_storage.h"

/* Private variables */
static UART_HandleTypeDef huart1;
static UART_HandleTypeDef huart3;
static SPI_HandleTypeDef hspi1;
static TIM_HandleTypeDef htim1;
static TIM_HandleTypeDef htim2;

/**
 * Main function
 */
int main(void)
{
    /* Reset of all peripherals, Initializes the Flash interface and the Systick */
    HAL_Init();
    
    /* Configure the system clock */
    SystemClock_Config();
    
    /* Initialize GPIO */
    MX_GPIO_Init();
    
    /* Initialize UART for PC communication */
    uart_pc_init();
    
    /* Initialize UART for FPGA communication */
    uart_fpga_init();
    
    /* Initialize SPI for potential future use */
    MX_SPI1_Init();
    
    /* Initialize motor control for 5 axes */
    motor_init();
    motor_enable();
    
    /* Initialize sensors for 5 axes */
    sensor_init();
    
    /* Initialize FPGA interface */
    fpga_init();
    
    /* Initialize G-code storage */
    gcode_storage_init();
    
    /* Send startup message */
    uart_send_string(&huart1, "CNC 5-Axis Controller Started\r\n");
    uart_send_string(&huart1, "Axes: X, Y, Z, A(rotation-X), B(rotation-Y)\r\n");
    
    /* Main loop */
    while (1)
    {
        /* Update motor positions */
        motor_update();
        
        /* Update sensor states */
        sensor_update();
        
        /* Check for emergency stop condition */
        if (sensor_is_triggered(SENSOR_X_ENDSTOP) ||
            sensor_is_triggered(SENSOR_Y_ENDSTOP) ||
            sensor_is_triggered(SENSOR_Z_ENDSTOP) ||
            sensor_is_triggered(SENSOR_A_ENDSTOP) ||
            sensor_is_triggered(SENSOR_B_ENDSTOP))
        {
            motor_emergency_stop();
            gcode_storage_stop_program();
            uart_send_string(&huart1, "EMERGENCY STOP - Endstop triggered!\r\n");
        }
        
        /* Process G-code program if running */
        if (gcode_storage_is_program_running()) {
            char* gcode_line = gcode_storage_get_next_line();
            if (gcode_line != NULL) {
                /* Send command status */
                uart_send_string(&huart1, "Executing: ");
                uart_send_string(&huart1, gcode_line);
                uart_send_string(&huart1, "\r\n");
                
                /* Parse and execute G-code */
                /* TODO: Implement G-code parser and executor */
            } else {
                uart_send_string(&huart1, "Program completed\r\n");
            }
        }
        
        HAL_Delay(10);
    }
    
    return 0;
}

/**
 * System Clock Configuration
 */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    /* Supply configuration update enable */
    HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);
    
    /* Configure the main internal regulator output voltage */
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);
    
    while(!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}
    
    /* Initializes the RCC Oscillators */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSIDiv = RCC_HSI_DIV1;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM = 4;
    RCC_OscInitStruct.PLL.PLLN = 60;
    RCC_OscInitStruct.PLL.PLLP = 2;
    RCC_OscInitStruct.PLL.PLLQ = 2;
    RCC_OscInitStruct.PLL.PLLR = 2;
    RCC_OscInitStruct.PLL.PLLRGE = RCC_PLL1VCIRANGE_3;
    RCC_OscInitStruct.PLL.PLLVCOSEL = RCC_PLL1VCOWIDE;
    RCC_OscInitStruct.PLL.PLLFRACN = 0;
    
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }
    
    /* Initializes the CPU, AHB and APB buses clocks */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
                                |RCC_CLOCKTYPE_D3PCLK1|RCC_CLOCKTYPE_D1PCLK1;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB3CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB4CLKDivider = RCC_HCLK_DIV2;
    
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK) {
        Error_Handler();
    }
}

/**
 * GPIO Initialization
 */
void MX_GPIO_Init(void)
{
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
}

/**
 * UART1 Initialization
 */
void MX_UART1_Init(void)
{
    huart1.Instance = USART1;
    huart1.Init.BaudRate = UART_PC_BAUDRATE;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart1);
}

/**
 * UART3 Initialization
 */
void MX_UART3_Init(void)
{
    huart3.Instance = USART3;
    huart3.Init.BaudRate = UART_FPGA_BAUDRATE;
    huart3.Init.WordLength = UART_WORDLENGTH_8B;
    huart3.Init.StopBits = UART_STOPBITS_1;
    huart3.Init.Parity = UART_PARITY_NONE;
    huart3.Init.Mode = UART_MODE_TX_RX;
    huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart3.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart3);
}

/**
 * SPI1 Initialization (for potential future use)
 */
void MX_SPI1_Init(void)
{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_2;
    HAL_SPI_Init(&hspi1);
}

/**
 * Error Handler
 */
void Error_Handler(void)
{
    while (1) {
        HAL_Delay(100);
    }
}

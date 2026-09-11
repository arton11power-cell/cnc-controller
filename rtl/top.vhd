library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top is
    port (
        -- Clock and reset
        clk         : in  std_logic;  -- 50 MHz
        rst_n       : in  std_logic;  -- Active low reset
        
        -- UART Interface (to STM32)
        uart_rx     : in  std_logic;
        uart_tx     : out std_logic;
        
        -- Motor outputs (5 axes)
        step_x      : out std_logic;
        dir_x       : out std_logic;
        step_y      : out std_logic;
        dir_y       : out std_logic;
        step_z      : out std_logic;
        dir_z       : out std_logic;
        step_a      : out std_logic;
        dir_a       : out std_logic;
        step_b      : out std_logic;
        dir_b       : out std_logic;
        
        -- Sensor inputs (endstops)
        endstop_x   : in  std_logic;
        endstop_y   : in  std_logic;
        endstop_z   : in  std_logic;
        endstop_a   : in  std_logic;
        endstop_b   : in  std_logic;
        
        -- Spindle and cooling control (PWM)
        pwm_spindle : out std_logic;
        pwm_cool    : out std_logic;
        
        -- Status LED
        led_status  : out std_logic
    );
end entity top;

architecture rtl of top is
    
    -- UART signals
    signal uart_rx_data     : std_logic_vector(7 downto 0);
    signal uart_rx_valid    : std_logic;
    signal uart_tx_data     : std_logic_vector(7 downto 0);
    signal uart_tx_valid    : std_logic;
    signal uart_tx_ready    : std_logic;
    
    -- Command decoder signals
    signal cmd_type         : std_logic_vector(7 downto 0);
    signal cmd_data_len     : std_logic_vector(15 downto 0);
    signal cmd_data         : std_logic_vector(255 downto 0);
    signal cmd_valid        : std_logic;
    
    -- Pulse generator signals
    signal pulse_x          : std_logic;
    signal pulse_y          : std_logic;
    signal pulse_z          : std_logic;
    signal pulse_a          : std_logic;
    signal pulse_b          : std_logic;
    
    signal dir_x_sig        : std_logic;
    signal dir_y_sig        : std_logic;
    signal dir_z_sig        : std_logic;
    signal dir_a_sig        : std_logic;
    signal dir_b_sig        : std_logic;
    
    -- Status signals
    signal status_word      : std_logic_vector(7 downto 0);
    signal error_status     : std_logic;
    
begin
    
    -- UART Interface
    uart_inst : entity work.uart_interface
        port map (
            clk         => clk,
            rst_n       => rst_n,
            uart_rx     => uart_rx,
            uart_tx     => uart_tx,
            rx_data     => uart_rx_data,
            rx_valid    => uart_rx_valid,
            tx_data     => uart_tx_data,
            tx_valid    => uart_tx_valid,
            tx_ready    => uart_tx_ready
        );
    
    -- Command Decoder
    cmd_decoder_inst : entity work.command_decoder
        port map (
            clk         => clk,
            rst_n       => rst_n,
            rx_data     => uart_rx_data,
            rx_valid    => uart_rx_valid,
            cmd_type    => cmd_type,
            cmd_data_len => cmd_data_len,
            cmd_data    => cmd_data,
            cmd_valid   => cmd_valid
        );
    
    -- Pulse Generator (5 axes)
    pulse_gen_x : entity work.pulse_generator
        port map (
            clk         => clk,
            rst_n       => rst_n,
            enable      => cmd_valid and (cmd_type = x"02"),
            frequency   => unsigned(cmd_data(15 downto 0)),
            duration    => unsigned(cmd_data(31 downto 16)),
            direction   => cmd_data(40),
            pulse_out   => pulse_x,
            dir_out     => dir_x_sig
        );
    
    pulse_gen_y : entity work.pulse_generator
        port map (
            clk         => clk,
            rst_n       => rst_n,
            enable      => cmd_valid and (cmd_type = x"02"),
            frequency   => unsigned(cmd_data(15 downto 0)),
            duration    => unsigned(cmd_data(31 downto 16)),
            direction   => cmd_data(41),
            pulse_out   => pulse_y,
            dir_out     => dir_y_sig
        );
    
    pulse_gen_z : entity work.pulse_generator
        port map (
            clk         => clk,
            rst_n       => rst_n,
            enable      => cmd_valid and (cmd_type = x"02"),
            frequency   => unsigned(cmd_data(15 downto 0)),
            duration    => unsigned(cmd_data(31 downto 16)),
            direction   => cmd_data(42),
            pulse_out   => pulse_z,
            dir_out     => dir_z_sig
        );
    
    pulse_gen_a : entity work.pulse_generator
        port map (
            clk         => clk,
            rst_n       => rst_n,
            enable      => cmd_valid and (cmd_type = x"02"),
            frequency   => unsigned(cmd_data(15 downto 0)),
            duration    => unsigned(cmd_data(31 downto 16)),
            direction   => cmd_data(43),
            pulse_out   => pulse_a,
            dir_out     => dir_a_sig
        );
    
    pulse_gen_b : entity work.pulse_generator
        port map (
            clk         => clk,
            rst_n       => rst_n,
            enable      => cmd_valid and (cmd_type = x"02"),
            frequency   => unsigned(cmd_data(15 downto 0)),
            duration    => unsigned(cmd_data(31 downto 16)),
            direction   => cmd_data(44),
            pulse_out   => pulse_b,
            dir_out     => dir_b_sig
        );
    
    -- PWM Controller
    pwm_ctrl_inst : entity work.pwm_controller
        port map (
            clk         => clk,
            rst_n       => rst_n,
            cmd_valid   => cmd_valid and (cmd_type = x"05"),
            pwm_ch1_val => unsigned(cmd_data(7 downto 0)),
            pwm_ch2_val => unsigned(cmd_data(15 downto 8)),
            pwm_out1    => pwm_spindle,
            pwm_out2    => pwm_cool
        );
    
    -- Status Monitor
    status_mon_inst : entity work.status_monitor
        port map (
            clk         => clk,
            rst_n       => rst_n,
            endstop_x   => endstop_x,
            endstop_y   => endstop_y,
            endstop_z   => endstop_z,
            endstop_a   => endstop_a,
            endstop_b   => endstop_b,
            status_word => status_word,
            error_status => error_status
        );
    
    -- Output assignments
    step_x  <= pulse_x;
    dir_x   <= dir_x_sig;
    step_y  <= pulse_y;
    dir_y   <= dir_y_sig;
    step_z  <= pulse_z;
    dir_z   <= dir_z_sig;
    step_a  <= pulse_a;
    dir_a   <= dir_a_sig;
    step_b  <= pulse_b;
    dir_b   <= dir_b_sig;
    
    -- Status LED
    led_status <= not error_status;
    
end architecture rtl;

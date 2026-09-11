library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity pwm_controller is
    generic (
        CLK_FREQ    : natural := 50_000_000;  -- 50 MHz
        PWM_FREQ    : natural := 20000        -- 20 kHz
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        cmd_valid   : in  std_logic;
        pwm_ch1_val : in  unsigned(7 downto 0);  -- 0-255
        pwm_ch2_val : in  unsigned(7 downto 0);  -- 0-255
        pwm_out1    : out std_logic;
        pwm_out2    : out std_logic
    );
end entity pwm_controller;

architecture rtl of pwm_controller is
    
    constant PWM_DIV : natural := CLK_FREQ / PWM_FREQ / 256;
    
    signal counter      : natural range 0 to PWM_DIV - 1 := 0;
    signal pwm_counter  : unsigned(7 downto 0) := (others => '0');
    signal ch1_val      : unsigned(7 downto 0) := (others => '0');
    signal ch2_val      : unsigned(7 downto 0) := (others => '0');
    
begin
    
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            counter <= 0;
            pwm_counter <= (others => '0');
            ch1_val <= (others => '0');
            ch2_val <= (others => '0');
            
        elsif rising_edge(clk) then
            
            -- Latch new values when command is valid
            if cmd_valid = '1' then
                ch1_val <= pwm_ch1_val;
                ch2_val <= pwm_ch2_val;
            end if;
            
            -- PWM counter
            if counter = PWM_DIV - 1 then
                counter <= 0;
                pwm_counter <= pwm_counter + 1;
            else
                counter <= counter + 1;
            end if;
        end if;
    end process;
    
    -- PWM outputs
    pwm_out1 <= '1' when pwm_counter < ch1_val else '0';
    pwm_out2 <= '1' when pwm_counter < ch2_val else '0';
    
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity pulse_generator is
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        enable      : in  std_logic;
        frequency   : in  unsigned(15 downto 0);  -- in Hz
        duration    : in  unsigned(15 downto 0);  -- in ms
        direction   : in  std_logic;
        pulse_out   : out std_logic;
        dir_out     : out std_logic
    );
end entity pulse_generator;

architecture rtl of pulse_generator is
    
    signal counter          : unsigned(31 downto 0) := (others => '0');
    signal pulse_counter    : unsigned(31 downto 0) := (others => '0');
    signal pulse_period     : unsigned(31 downto 0);
    signal is_running       : std_logic := '0';
    signal pulse_active     : std_logic := '0';
    signal duration_counter : unsigned(31 downto 0) := (others => '0');
    
begin
    
    -- Calculate pulse period: 50MHz / (2 * frequency)
    pulse_period <= to_unsigned(50000000, 32) / (frequency & "00" + 1);
    
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            counter <= (others => '0');
            pulse_counter <= (others => '0');
            is_running <= '0';
            pulse_active <= '0';
            duration_counter <= (others => '0');
            
        elsif rising_edge(clk) then
            
            -- Start generation
            if enable = '1' and is_running = '0' then
                is_running <= '1';
                counter <= (others => '0');
                duration_counter <= (others => '0');
                pulse_counter <= (others => '0');
                
            -- Generate pulses
            elsif is_running = '1' then
                counter <= counter + 1;
                
                -- Check if duration exceeded
                if duration_counter >= (unsigned(duration) * 50000) then
                    is_running <= '0';
                    pulse_active <= '0';
                else
                    duration_counter <= duration_counter + 1;
                    
                    -- Generate pulse
                    if counter >= pulse_period then
                        counter <= (others => '0');
                        pulse_active <= not pulse_active;
                    end if;
                end if;
            end if;
        end if;
    end process;
    
    pulse_out <= pulse_active and is_running;
    dir_out <= direction;
    
end architecture rtl;

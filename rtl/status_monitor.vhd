library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity status_monitor is
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        endstop_x   : in  std_logic;
        endstop_y   : in  std_logic;
        endstop_z   : in  std_logic;
        endstop_a   : in  std_logic;
        endstop_b   : in  std_logic;
        status_word : out std_logic_vector(7 downto 0);
        error_status : out std_logic
    );
end entity status_monitor;

architecture rtl of status_monitor is
    
    signal endstop_sync_x   : std_logic_vector(2 downto 0) := "111";
    signal endstop_sync_y   : std_logic_vector(2 downto 0) := "111";
    signal endstop_sync_z   : std_logic_vector(2 downto 0) := "111";
    signal endstop_sync_a   : std_logic_vector(2 downto 0) := "111";
    signal endstop_sync_b   : std_logic_vector(2 downto 0) := "111";
    
    signal endstop_x_edge   : std_logic := '0';
    signal endstop_y_edge   : std_logic := '0';
    signal endstop_z_edge   : std_logic := '0';
    signal endstop_a_edge   : std_logic := '0';
    signal endstop_b_edge   : std_logic := '0';
    
    signal error_status_reg : std_logic := '0';
    
begin
    
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            endstop_sync_x <= "111";
            endstop_sync_y <= "111";
            endstop_sync_z <= "111";
            endstop_sync_a <= "111";
            endstop_sync_b <= "111";
            endstop_x_edge <= '0';
            endstop_y_edge <= '0';
            endstop_z_edge <= '0';
            endstop_a_edge <= '0';
            endstop_b_edge <= '0';
            error_status_reg <= '0';
            
        elsif rising_edge(clk) then
            
            -- Synchronizers (3-stage)
            endstop_sync_x <= endstop_sync_x(1 downto 0) & endstop_x;
            endstop_sync_y <= endstop_sync_y(1 downto 0) & endstop_y;
            endstop_sync_z <= endstop_sync_z(1 downto 0) & endstop_z;
            endstop_sync_a <= endstop_sync_a(1 downto 0) & endstop_a;
            endstop_sync_b <= endstop_sync_b(1 downto 0) & endstop_b;
            
            -- Edge detection
            if endstop_sync_x(2) = '0' and endstop_sync_x(1) = '1' then
                endstop_x_edge <= '1';
                error_status_reg <= '1';
            else
                endstop_x_edge <= '0';
            end if;
            
            if endstop_sync_y(2) = '0' and endstop_sync_y(1) = '1' then
                endstop_y_edge <= '1';
                error_status_reg <= '1';
            else
                endstop_y_edge <= '0';
            end if;
            
            if endstop_sync_z(2) = '0' and endstop_sync_z(1) = '1' then
                endstop_z_edge <= '1';
                error_status_reg <= '1';
            else
                endstop_z_edge <= '0';
            end if;
            
            if endstop_sync_a(2) = '0' and endstop_sync_a(1) = '1' then
                endstop_a_edge <= '1';
                error_status_reg <= '1';
            else
                endstop_a_edge <= '0';
            end if;
            
            if endstop_sync_b(2) = '0' and endstop_sync_b(1) = '1' then
                endstop_b_edge <= '1';
                error_status_reg <= '1';
            else
                endstop_b_edge <= '0';
            end if;
        end if;
    end process;
    
    status_word(0) <= endstop_x_edge;
    status_word(1) <= endstop_y_edge;
    status_word(2) <= endstop_z_edge;
    status_word(3) <= endstop_a_edge;
    status_word(4) <= endstop_b_edge;
    status_word(5) <= '0';
    status_word(6) <= '0';
    status_word(7) <= '0';
    
    error_status <= error_status_reg;
    
end architecture rtl;

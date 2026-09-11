library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity command_decoder is
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        rx_data     : in  std_logic_vector(7 downto 0);
        rx_valid    : in  std_logic;
        cmd_type    : out std_logic_vector(7 downto 0);
        cmd_data_len : out std_logic_vector(15 downto 0);
        cmd_data    : out std_logic_vector(255 downto 0);
        cmd_valid   : out std_logic
    );
end entity command_decoder;

architecture rtl of command_decoder is
    
    type state_type is (IDLE, WAIT_CMD, WAIT_LEN_L, WAIT_LEN_H, WAIT_DATA, EXECUTE);
    signal state : state_type := IDLE;
    
    signal cmd_type_reg     : std_logic_vector(7 downto 0);
    signal cmd_len_l        : std_logic_vector(7 downto 0);
    signal cmd_len_h        : std_logic_vector(7 downto 0);
    signal data_counter     : natural range 0 to 256 := 0;
    signal cmd_data_reg     : std_logic_vector(255 downto 0);
    signal sync_byte        : std_logic_vector(7 downto 0);
    signal cmd_valid_reg    : std_logic := '0';
    
begin
    
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            state <= IDLE;
            cmd_type_reg <= (others => '0');
            cmd_len_l <= (others => '0');
            cmd_len_h <= (others => '0');
            data_counter <= 0;
            cmd_data_reg <= (others => '0');
            sync_byte <= (others => '0');
            cmd_valid_reg <= '0';
            
        elsif rising_edge(clk) then
            cmd_valid_reg <= '0';
            
            case state is
                when IDLE =>
                    if rx_valid = '1' and rx_data = x"AA" then
                        state <= WAIT_CMD;
                    end if;
                
                when WAIT_CMD =>
                    if rx_valid = '1' then
                        cmd_type_reg <= rx_data;
                        state <= WAIT_LEN_L;
                    end if;
                
                when WAIT_LEN_L =>
                    if rx_valid = '1' then
                        cmd_len_l <= rx_data;
                        state <= WAIT_LEN_H;
                    end if;
                
                when WAIT_LEN_H =>
                    if rx_valid = '1' then
                        cmd_len_h <= rx_data;
                        data_counter <= 0;
                        cmd_data_reg <= (others => '0');
                        
                        if unsigned(cmd_len_l) = 0 and unsigned(cmd_len_h) = 0 then
                            state <= EXECUTE;
                        else
                            state <= WAIT_DATA;
                        end if;
                    end if;
                
                when WAIT_DATA =>
                    if rx_valid = '1' then
                        -- Store data byte
                        cmd_data_reg(8 * (data_counter + 1) - 1 downto 8 * data_counter) <= rx_data;
                        data_counter <= data_counter + 1;
                        
                        -- Check if all data received
                        if data_counter = to_integer(unsigned(cmd_len_l)) - 1 then
                            state <= EXECUTE;
                        end if;
                    end if;
                
                when EXECUTE =>
                    cmd_valid_reg <= '1';
                    state <= IDLE;
                
            end case;
        end if;
    end process;
    
    cmd_type <= cmd_type_reg;
    cmd_data_len <= cmd_len_h & cmd_len_l;
    cmd_data <= cmd_data_reg;
    cmd_valid <= cmd_valid_reg;
    
end architecture rtl;

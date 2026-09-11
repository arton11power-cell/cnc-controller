library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity uart_interface is
    generic (
        CLK_FREQ    : natural := 50_000_000;  -- 50 MHz
        BAUD_RATE   : natural := 921600       -- 921600 baud
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        uart_rx     : in  std_logic;
        uart_tx     : out std_logic;
        rx_data     : out std_logic_vector(7 downto 0);
        rx_valid    : out std_logic;
        tx_data     : in  std_logic_vector(7 downto 0);
        tx_valid    : in  std_logic;
        tx_ready    : out std_logic
    );
end entity uart_interface;

architecture rtl of uart_interface is
    
    constant BAUD_DIV : natural := CLK_FREQ / BAUD_RATE;
    
    -- RX signals
    signal rx_clk_counter   : natural range 0 to BAUD_DIV - 1 := 0;
    signal rx_bit_counter   : natural range 0 to 10 := 0;
    signal rx_data_reg      : std_logic_vector(7 downto 0);
    signal rx_valid_reg     : std_logic := '0';
    signal uart_rx_sync     : std_logic_vector(2 downto 0) := "111";
    
    -- TX signals
    signal tx_clk_counter   : natural range 0 to BAUD_DIV - 1 := 0;
    signal tx_bit_counter   : natural range 0 to 10 := 0;
    signal tx_data_reg      : std_logic_vector(9 downto 0);
    signal tx_active        : std_logic := '0';
    signal tx_ready_sig     : std_logic := '1';
    
begin
    
    -- RX Process
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            rx_clk_counter <= 0;
            rx_bit_counter <= 0;
            rx_data_reg <= (others => '0');
            rx_valid_reg <= '0';
            uart_rx_sync <= "111";
            
        elsif rising_edge(clk) then
            rx_valid_reg <= '0';
            uart_rx_sync <= uart_rx_sync(1 downto 0) & uart_rx;
            
            if uart_rx_sync(2) = '0' and rx_bit_counter = 0 then
                -- Start bit detected
                rx_bit_counter <= 1;
                rx_clk_counter <= 0;
            
            elsif rx_bit_counter > 0 and rx_bit_counter < 10 then
                if rx_clk_counter = BAUD_DIV - 1 then
                    rx_clk_counter <= 0;
                    
                    if rx_bit_counter < 9 then
                        rx_data_reg(rx_bit_counter - 1) <= uart_rx_sync(2);
                    end if;
                    
                    rx_bit_counter <= rx_bit_counter + 1;
                else
                    rx_clk_counter <= rx_clk_counter + 1;
                end if;
            
            elsif rx_bit_counter = 10 then
                if rx_clk_counter = BAUD_DIV - 1 then
                    rx_valid_reg <= '1';
                    rx_bit_counter <= 0;
                else
                    rx_clk_counter <= rx_clk_counter + 1;
                end if;
            end if;
        end if;
    end process;
    
    -- TX Process
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            tx_clk_counter <= 0;
            tx_bit_counter <= 0;
            tx_data_reg <= (others => '1');
            tx_active <= '0';
            tx_ready_sig <= '1';
            
        elsif rising_edge(clk) then
            if tx_valid = '1' and tx_ready_sig = '1' then
                tx_data_reg <= '1' & tx_data & '0';  -- Stop bit, data, start bit
                tx_active <= '1';
                tx_bit_counter <= 0;
                tx_clk_counter <= 0;
                tx_ready_sig <= '0';
            
            elsif tx_active = '1' then
                if tx_clk_counter = BAUD_DIV - 1 then
                    tx_clk_counter <= 0;
                    
                    if tx_bit_counter = 9 then
                        tx_active <= '0';
                        tx_ready_sig <= '1';
                    else
                        tx_bit_counter <= tx_bit_counter + 1;
                    end if;
                else
                    tx_clk_counter <= tx_clk_counter + 1;
                end if;
            end if;
        end if;
    end process;
    
    uart_tx <= tx_data_reg(0) when tx_active = '1' else '1';
    rx_data <= rx_data_reg;
    rx_valid <= rx_valid_reg;
    tx_ready <= tx_ready_sig;
    
end architecture rtl;

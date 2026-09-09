# UART RX has no fixed phase relationship to clk. Only the path from the
# external pin to the first synchronizer D pin is asynchronous. Keep the
# rx_sync1 -> rx_sync2 path and all downstream logic timed.
# Resolve the register from its retained RTL net name, never a synthesized
# instance number. Fail closed if synthesis changes this structure.
set uart_rx_port [get_ports {gpio_bot_in[0]}]
set uart_sync1_net [get_nets -quiet {u_npu_sys.u_uart_apb.u_bridge.u_uart_rx.rx_sync1}]
set uart_sync2_net [get_nets -quiet {u_npu_sys.u_uart_apb.u_bridge.u_uart_rx.rx_sync2}]
if {[llength $uart_rx_port] != 1 || [llength $uart_sync1_net] != 1 || [llength $uart_sync2_net] != 1} {
    error "Expected UART RX port and two synchronizer nets"
}
set uart_sync1_q [get_pins -of_objects $uart_sync1_net -filter {direction == output}]
set uart_sync1_cell [get_cells -of_objects $uart_sync1_q]
if {[llength $uart_sync1_cell] != 1} {
    error "Expected one driver for UART rx_sync1"
}
set uart_sync1_d [get_pins -quiet [get_full_name $uart_sync1_cell]/D]
if {[llength $uart_sync1_d] != 1} {
    error "Expected UART rx_sync1 register D pin"
}
set_false_path -from $uart_rx_port -to $uart_sync1_d
puts "UART async exception: gpio_bot_in\[0\] -> [get_full_name $uart_sync1_d]"

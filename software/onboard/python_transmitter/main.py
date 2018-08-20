import protocols
import connection
import packet_formats
import time
import machine
import gc
import time


LOOP_TIME_US = 16000  # ~ 60Hz

def send_control_packet(comms):
    joy1x = machine.ADC(machine.Pin(32))
    joy1y = machine.ADC(machine.Pin(33))
    joy2x = machine.ADC(machine.Pin(34))
    joy2y = machine.ADC(machine.Pin(35))
    
    joy1x.atten(joy1x.ATTN_11DB)
    joy1y.atten(joy1y.ATTN_11DB)
    joy2x.atten(joy2x.ATTN_11DB)
    joy2y.atten(joy2y.ATTN_11DB)
    
    
    control_packet = packet_formats.ControlPacket()
        
    while(1):
        control_packet.val1 = 2048 - joy1x.read()
        control_packet.val2 = 2048 - joy1y.read()
        control_packet.val3 = 2048 - joy2x.read()
        control_packet.val4 = 2048 - joy2y.read()
        
        comms.send_packet(control_packet)
        yield 1


def print_loop_time():
    prev_time = time.ticks_ms()
    counter = 0
    while(1):
        cur_time = time.ticks_ms()
        counter += 1
        delta = cur_time - prev_time
        if delta > 1000:
            prev_time = cur_time
            print("Loop rate:", (1000 / delta) * counter)
            counter = 0
        yield 1


def start():
    connection.init()
    comms = protocols.ConnectionHandler(connection)
    
    
    tasks = [
        send_control_packet(comms),
        print_loop_time()
    ]
    sleep_time = time.ticks_us()
    while(1):
        for task in tasks:
            next(task)
        
        gc.collect()
        sleep_time = LOOP_TIME_US - (time.ticks_us() - sleep_time)
        if sleep_time > 0:
            time.sleep_us(sleep_time)
        sleep_time = time.ticks_us()


if __name__ == "__main__":
    start()

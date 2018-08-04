#include "servo.h"
#include "dynamixel_crc.h"
#include "driver/uart.h"
#include <string.h>
#include "xl320.h"

#define UART_GPIO_PIN GPIO_NUM_16
#define UART_MODULE UART_NUM_1
#define RX_BUFFER_SIZE (128)

#define TX_MAX_DATA 10


typedef enum {
	XL320_LED_COLOR = 0x19,
	XL320_SERVO_ID = 0x03,
	XL320_RETURN_DELAY = 0x05,
	XL320_BAUD_RATE = 0x04,
	XL320_GOAL_POSITION = 0x1E,
	XL320_PRESENT_POSITION = 0x25,
} XL320_Registers;


typedef enum {
	SERVO_ID = 4,
	PACKET_LEN_L = 5,
	PACKET_LEN_H = 6,
	PACKET_TYPE = 7,
	DATA_START = 8,
	HEADER_SIZE = 8,
} TX_PacketOffset;

typedef enum {
	PACKET_WRITE = 0x03,
	PACKET_READ = 0x02,
} TX_PacketTypes;

uint8_t tx_packet_buffer[DATA_START + TX_MAX_DATA + 2] = {  // The 2 is for the crc
	0xFF, 0xFF, 0xFD, 0x00,  // Header. All the rest is set each send
};

uint8_t rx_buffer[20] = {0};
uint8_t* rx_data_start;
uint16_t  rx_data_len = 0;



ServoResponse servo_init(void){
	// Configure UART
	uart_config_t uart_config = {
        .baud_rate = 1000000,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    ESP_ERROR_CHECK(uart_param_config(UART_MODULE, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(
		UART_MODULE,
		GPIO_NUM_16,
		GPIO_NUM_17,
		UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE
	));

    ESP_ERROR_CHECK(uart_driver_install(UART_MODULE, RX_BUFFER_SIZE*2, 0, 0, NULL, 0));

	rx_data_start = rx_buffer + DATA_START + 1;

    return SERVO_OK;
}



ServoResponse dynamixel_send(uint8_t servo_id, TX_PacketTypes packet_type, uint8_t* parameters, uint8_t parameters_len){
	/* Writes to various registers on the servo bus */
	if (parameters_len > TX_MAX_DATA){
		return SERVO_COMM_ERROR;
	}
	
	tx_packet_buffer[SERVO_ID] = servo_id;
	tx_packet_buffer[PACKET_LEN_L] = (parameters_len + 3);
	tx_packet_buffer[PACKET_LEN_H] = (parameters_len + 3) >> 8;
	tx_packet_buffer[PACKET_TYPE] = packet_type;
	for (uint8_t i=0; i<parameters_len; i++){
		tx_packet_buffer[DATA_START+i] = parameters[i];
	}
	uint16_t crc = dynamixel_crc((unsigned char*)tx_packet_buffer, HEADER_SIZE + parameters_len);
	tx_packet_buffer[HEADER_SIZE + parameters_len + 0] = (uint8_t)crc;
	tx_packet_buffer[HEADER_SIZE + parameters_len + 1] = (uint8_t)(crc >> 8);
	
	uart_tx_chars(UART_MODULE, (char*)tx_packet_buffer, HEADER_SIZE + parameters_len + 2);

	// Wait until sent, then clear the current RX buffer
	uart_wait_tx_done(UART_MODULE, 10 / portTICK_PERIOD_MS); // Timeout in RTOS ticks
	uart_flush(UART_MODULE);
	
	rx_data_len = 0;
	uint16_t read_count = uart_read_bytes(UART_MODULE, rx_buffer, sizeof(rx_buffer), 10 / portTICK_PERIOD_MS);
	if (read_count < DATA_START){
		// Not enough data
		return SERVO_COMM_ERROR;
	}
	if (memcmp(rx_buffer, tx_packet_buffer, 4) != 0){
		// Header is incorrect
		return SERVO_COMM_ERROR;
	}
	if (rx_buffer[SERVO_ID] != servo_id){
		// Wrong Servo?!
		return SERVO_COMM_ERROR;
	}
	if (rx_buffer[PACKET_TYPE] != 0x55){
		// Not a status packet
		return SERVO_COMM_ERROR;
	}
	uint8_t error_byte = rx_buffer[PACKET_TYPE+1];
	/* if ((error_byte & (1<<7)) != 0x00){
		// The servo has some sort of error
		return SERVO_HARDWARE_ERROR;
	} */
	if ((error_byte & (~(1<<7))) != 0x00){
		// Servo reports the sent packet has invalid crc etc.
		return SERVO_COMM_ERROR;
	}
	
	uint16_t raw_packet_size = rx_buffer[PACKET_LEN_L] + (rx_buffer[PACKET_LEN_H] << 8);
	if ((rx_data_len) > sizeof(rx_buffer) - 10){
		//Packet Overflow
		return SERVO_COMM_ERROR;
	}
	uint16_t packet_end = raw_packet_size + DATA_START - 1;
	uint16_t got_crc = rx_buffer[packet_end-2] + (rx_buffer[packet_end-1] << 8);
	uint16_t computed_crc = dynamixel_crc((unsigned char*)rx_buffer, packet_end-2);
	
	if (got_crc != computed_crc){
		return SERVO_COMM_ERROR;
	}
	
	rx_data_len = raw_packet_size - 4; // Remove the CRC (2bytes), hardware status, and packet type

	return SERVO_OK;
}


ServoResponse servo_set_position(uint8_t servo_id, float radians){
	float degrees = radians * 180.0 / 3.14159 ;
	uint16_t ticks = 512.0 + (degrees * (1/0.29));  // radians per tick
	if (ticks > 1024){
		return SERVO_PARAM_ERROR;
	}
	uint8_t data[4] = {0};
	data[0] = XL320_GOAL_POSITION;
	data[1] = 0x00;
	data[2] = ticks;
	data[3] = ticks >> 8;
	
	return dynamixel_send(
		servo_id, PACKET_WRITE, data, sizeof(data)
	);
}


ServoResponse servo_get_position(uint8_t servo_id, float* radians){
	uint8_t data[4] = {0};
	data[0] = XL320_PRESENT_POSITION;
	data[1] = 0x00;
	data[2] = 0x02;  // Read two bytes
	data[3] = 0x00;
	
	ServoResponse res = dynamixel_send(
		servo_id, PACKET_READ, data, sizeof(data)
	);
	if (res == SERVO_OK){
		if (rx_data_len != 2){
			return SERVO_COMM_ERROR;
		}
		int16_t ticks = rx_data_start[0] + (rx_data_start[1] << 8);
		float degrees = (float)(ticks - 512) * 0.29;
		*radians = degrees * (3.14159 / 180.0);
	}
	return res;
}


ServoResponse servo_set_led(uint8_t servo_id, ServoColor color){
	uint8_t data[3] = {0};
	data[0] = XL320_LED_COLOR;
	data[1] = 0x00;
	data[2] = color;
	return dynamixel_send(
		servo_id, PACKET_WRITE, data, sizeof(data)
	);
}

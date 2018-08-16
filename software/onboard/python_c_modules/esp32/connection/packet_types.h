#ifndef __packet_types_h__
#define __packet_types_h__

#include <stdint.h>


#define VAR_VAL_MAX_NAME_LEN 10
#define LOG_MAX_MESSAGE_LEN 50

typedef struct {
	uint16_t linear_velocity_x;
	uint16_t linear_velocity_y;
	uint16_t angular_velocity_z;
	uint16_t turret_elevation_velocity;
	uint16_t turret_pan_velocity;
	uint8_t bullet_id;
	uint8_t gun_enabled;
} control_packet_t;


typedef enum {
	DEBUG = 0;
	INFO = 1;
	WARNING = 2;
	ERROR = 3;
	CRITICAL = 4;
	OK = 5;
} message_status_t;


typedef struct {
	message_status_t status; 
	uint32_t value;
	uint8[VAR_VAL_MAX_NAME_LEN] name;
} var_val_t;


typedef struct {
	message_status_t status;
	uint8_t message_len;
	uint8_t[LOG_MAX_MESSAGE_LEN] message;
}

#endif

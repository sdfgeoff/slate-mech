#ifndef __dynamixel_h__
#define __dynamixel_h__

#include <stdint.h>

typedef enum {
	SERVO_OK = 0,  // Successfully completed operation
	SERVO_PARAM_ERROR = 1,  // Error with function parameters (eg motion out of range)
	SERVO_COMM_ERROR = 2,  // Error with communication (eg timeout)
	SERVO_HARDWARE_ERROR = 3,  // Servo is reporting a hardware error
	SERVO_FAIL = 4,  // Unspecified error
} ServoResponse;

typedef enum {
	SERVO_RED = 1,
	SERVO_GREEN = 1<<1,
	SERVO_BLUE = 1<<2,
} ServoColor;

extern ServoResponse servo_init();
extern ServoResponse servo_set_position(uint8_t servo_id, float radians);
extern ServoResponse servo_get_position(uint8_t servo_id, float* radians);
extern ServoResponse servo_set_led(uint8_t servo_id, ServoColor value);

#endif

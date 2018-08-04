#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include <stdio.h>

#include "xl320.h"

/* This python module exposes all functions that talk to the actuators and
 * sensors on board the robot */

STATIC mp_obj_t chassis_init(void) {
    servo_init();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(chassis_init_obj, chassis_init);


STATIC mp_obj_t chassis_servo_set_position(mp_obj_t address, mp_obj_t position) {
    servo_set_position(mp_obj_get_int(address), mp_obj_get_float(position));
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(chassis_servo_set_position_obj, chassis_servo_set_position);


STATIC const mp_map_elem_t chassis_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_chassis) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_init), (mp_obj_t)&chassis_init_obj },
    { MP_OBJ_NEW_QSTR(MP_QSTR_servo_set_position), (mp_obj_t)&chassis_servo_set_position_obj },
};



STATIC MP_DEFINE_CONST_DICT (
    mp_module_chassis_globals,
    chassis_globals_table
);

const mp_obj_module_t mp_module_chassis = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_chassis_globals,
};


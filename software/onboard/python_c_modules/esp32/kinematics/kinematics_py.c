#include "kinematics.h"
#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include <stdio.h>

STATIC mp_obj_t kinematics_forward(mp_obj_t shoulder_radians, mp_obj_t elbow_radians, mp_obj_t wrist_radians) {
    float x, y, z = 0.0;
    forward_kinematics(
        mp_obj_get_float(shoulder_radians), mp_obj_get_float(elbow_radians), mp_obj_get_float(wrist_radians),
        &x, &y, &z
    );
    mp_obj_t tuple[3];
    tuple[0] = mp_obj_new_float(x);
    tuple[1] = mp_obj_new_float(y);
    tuple[2] = mp_obj_new_float(z);
    return mp_obj_new_tuple(3, tuple);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(kinematics_forward_obj, kinematics_forward);


STATIC mp_obj_t kinematics_inverse(mp_obj_t target_position, mp_obj_t flip) {
    mp_obj_t* positions;
    mp_obj_get_array_fixed_n(target_position, 3, &positions);
    
    float shoulder, elbow, wrist = 0.0;
    inverse_kinematics(
        mp_obj_get_float(positions[0]), mp_obj_get_float(positions[1]), mp_obj_get_float(positions[2]),
        mp_obj_get_float(flip),
        &shoulder, &elbow, &wrist
    );
    mp_obj_t tuple[3];
    tuple[0] = mp_obj_new_float(shoulder);
    tuple[1] = mp_obj_new_float(elbow);
    tuple[2] = mp_obj_new_float(wrist);
    return mp_obj_new_tuple(3, tuple);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(kinematics_inverse_obj, kinematics_inverse);


STATIC const mp_map_elem_t kinematics_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_kinematics) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_forward), (mp_obj_t)&kinematics_forward_obj },
    { MP_OBJ_NEW_QSTR(MP_QSTR_inverse), (mp_obj_t)&kinematics_inverse_obj },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_kinematics_globals,
    kinematics_globals_table
);

const mp_obj_module_t kinematics_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_kinematics_globals,
};

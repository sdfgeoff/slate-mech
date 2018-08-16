#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include <stdio.h>
#include "string.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_wifi.h"
#include "esp_event_loop.h"

#include "tranceiver.h"

/* This python module exposes all functions that talk to the actuators and
 * sensors on board the robot */

static QueueHandle_t rx_packet_queue;

STATIC mp_obj_t connection_init(void) {
    tranceiver_init();

    rx_packet_queue = xQueueCreate(2, TRANCEIVER_MIN_QUEUE_SIZE + TRANCEIVER_MAX_PACKET_BYTES);
    tranceiver_set_queue(rx_packet_queue);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(connection_init_obj, connection_init);


STATIC mp_obj_t connection_get_latest_packet(void) {
    uint8_t latest_packet_raw[TRANCEIVER_MIN_QUEUE_SIZE + TRANCEIVER_MAX_PACKET_BYTES] = {0};
    tranceiver_packet_stats* latest_packet = (tranceiver_packet_stats*)&latest_packet_raw;

    vstr_t in_data;

    if (xQueueReceive(rx_packet_queue, &latest_packet_raw, 0) == pdTRUE){
        vstr_init_len(&in_data, latest_packet->data_length);
        for (int i=0; i<latest_packet->data_length; i++){
            in_data.buf[i] = latest_packet->data[i];
        }
        return mp_obj_new_str_from_vstr(&mp_type_bytes, &in_data);
    } else {
        return mp_const_none;
    }
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(connection_get_latest_packet_obj, connection_get_latest_packet);


STATIC mp_obj_t connection_send_packet(mp_obj_t data_in) {
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(data_in, &bufinfo, MP_BUFFER_READ);

    if (tranceiver_send_packet(bufinfo.buf, bufinfo.len) != 0){
        return mp_const_false;
    } else {
        return mp_const_true;
    }
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(connection_send_packet_obj, connection_send_packet);




STATIC const mp_map_elem_t connection_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_connection) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_init), (mp_obj_t)&connection_init_obj },
    { MP_OBJ_NEW_QSTR(MP_QSTR_get_latest_packet), (mp_obj_t)&connection_get_latest_packet_obj },
    { MP_OBJ_NEW_QSTR(MP_QSTR_send_packet), (mp_obj_t)&connection_send_packet_obj },
};


STATIC MP_DEFINE_CONST_DICT (
    mp_module_connection_globals,
    connection_globals_table
);

const mp_obj_module_t connection_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_connection_globals,
};


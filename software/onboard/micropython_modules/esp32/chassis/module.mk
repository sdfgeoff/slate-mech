export SRC_MOD+= \
	chassis/chassis.c \
	chassis/dynamixel_crc.c \
	chassis/xl320.c \

export WEAK_LINKS += \
	{ MP_OBJ_NEW_QSTR(MP_QSTR_chassis), (mp_obj_t)&mp_module_chassis }, \

export EXTRA_MODULES += \
	extern const struct _mp_obj_module_t mp_module_chassis; \

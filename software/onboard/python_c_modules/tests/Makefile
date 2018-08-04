SRC_PATHS = . \
	../esp32/kinematics \
	../lib_ext/Unity/src \


SOURCES := $(foreach dir,$(SRC_PATHS),$(wildcard $(dir)/*.c))
#$(wildcard $(path)/*.c))
#SOURCES := $(wildcard ../esp32/kinematics/*.c)
OBJECTS := $(patsubst %.c, %.o, $(SOURCES))

INCLUDES = \
	-I../esp32 \
	-I../lib_ext/Unity/src \

LINKS = \
	-lm


build: $(OBJECTS)
	$(CC) $^ -o ./test $(LINKS)

%.o: %.c
	$(CC) $(INCLUDES)  -c $< -o $@ 


test: build
	./test


clean: 
	rm $(OBJECTS)

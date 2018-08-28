BASEDIR=$(CURDIR)

MAKE_FLAGS=IDF_PATH=$(BASEDIR)/esp-idf USER_C_MODULES=$(BASEDIR)/python_c_modules/esp32 FROZEN_MPY_DIR=$(BASEDIR)/python_frozen_modules

build:
	cd micropython/ports/esp32; \
	make $(MAKE_FLAGS); \
	mv ./build/application.bin $(BASEDIR)/

clean:
	cd micropython/ports/esp32; \
	make clean $(MAKE_FLAGS); \
	rm $(BASEDIR)/application.bin

flash: build
	cd micropython/ports/esp32; \
	make deploy $(MAKE_FLAGS);

monitor:
	miniterm.py /dev/ttyUSB0 115200


load_transmitter:
	python3 ./load.py --base_folder python_transmitter

load_receiver:
	python3 ./load.py --base_folder python_receiver

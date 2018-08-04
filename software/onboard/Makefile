BASEDIR=$(CURDIR)

MAKE_FLAGS=IDF_PATH=$(BASEDIR)/esp-idf USER_C_MODULES=$(BASEDIR)/python_c_modules/esp32 FROZEN_MPY_DIR=$(BASEDIR)/python


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

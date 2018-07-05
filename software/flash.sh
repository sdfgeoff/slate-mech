cd micropython/ports/esp32/; make ESPIDF=../../../esp-idf/
esptool --chip esp32 -p /dev/ttyUSB0 erase_flash
esptool --chip esp32 -p /dev/ttyUSB0 write_flash 0x1000 ./build/firmware.bin

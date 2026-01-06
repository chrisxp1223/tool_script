#!/bin/bash
board_name=$1
sku_name=$2
fw_type=$3
temp_location=$(pwd)/tmp
fw_src_location=/build/$1/firmware/


__get_fw_temp() {
	echo $1
	echo $2
	mkdir $temp_location
	if ["$fw_type" -ne 0 ]; then
		cp $(fw_src_location)/$(sku_name).bin temp_location
	else 
		cp $(fw_src_location)/$(sku_name).serial.bin temp_location
	fi
}


flash_main() {
	__get_fw_temp $board_name $sku_name $fw_type
#	dut-control spi2_buf_en:on spi2_buf_on_flex_en:on spi2_vref:pp1800 cold_reset:on
#	sudo flashrom -V -p ft2232_spi:type=servo-v2 -w $IMAGE [need to change for each servo type]
#	dut-control spi2_buf_en:off spi2_buf_on_flex_en:off spi2_vref:off cold_reset:off
}

################################################################################
#flsash star
flash_main



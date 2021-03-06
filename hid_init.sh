# #################################################################################
#
# Indoor system script
#	set USB audio defaults
#
# #################################################################################

HID=./hid
OUTPUT_CONTROL=0x1019
EQ_GAIN_LOW=0x10D7
EQ_GAIN_HIGH=0x10D8
DSP_ENABLE_R1=0x117A
DSP_ENABLE_R2=0x117B
DSP_INIT_1=0x117C
DSP_INIT_2=0x117D

$HID w $OUTPUT_CONTROL 0x88
$HID w $EQ_GAIN_LOW 0xB2
$HID w $EQ_GAIN_HIGH 0x3F
$HID w $DSP_ENABLE_R1 0x05
$HID w $DSP_INIT_2 0x1


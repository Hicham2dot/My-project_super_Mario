import datapacket
import datapacket


MAC_ADDRESS = "C5:B9:80:7F:FB:08"
DEVICE_CONFIG = [
    'DEMO 0',    
    'TXMEMS 2',  
    'TXECG 2',   
]
# LEGEND:
#   *_SERV --> services
#   *_CHAR --> characteristics
#   *_DESC --> descriptors

ACCESS_PROFILE_SERV = ("Generic Access Profile", "00001800-0000-1000-8000-00805f9b34fb", 1)
DEVICE_NAME_CHAR = ("Device Name","00002a00-0000-1000-8000-00805f9b34fb", 2)
APPEARANCE_CHAR = ("Appearance","00002a01-0000-1000-8000-00805f9b34fb", 4)
CONN_PARAMETERS_CHAR = ("Peripheral Preferred Connection Parameters","00002a04-0000-1000-8000-00805f9b34fb", 6)
ADDRESS_RESOLUTION_CHAR = ("Central Address Resolution","00002aa6-0000-1000-8000-00805f9b34fb", 8)

ATTRIBUTE_PROFILE_SERV = ("Generic Attribute Profile", "00001801-0000-1000-8000-00805f9b34fb", 10)

UNKNOWN_SERV = ("Unknown", "b3ad0001-67ba-a4ea-2d8a-328fc521ab34", 11)
REVISION_CHAR = ("Software Revision String", "00002a28-0000-1000-8000-00805f9b34fb", 12)
DATE_CHAR =  ("Date Time", "00002a08-0000-1000-8000-00805f9b34fb", 14)
BATTERY_CHAR = ("Battery","00002a19-0000-1000-8000-00805f9b34fb", 17)
TEMP_CHAR = ("Temperature","00002a6e-0000-1000-8000-00805f9b34fb", 19)
HR_CHAR =  ("Heart Rate", "00002a37-0000-1000-8000-00805f9b34fb", 22)
BTH1_CHAR = ("Breath Rate 1","00002a3d-0000-1000-8000-00805f9b34fb", 25)
BTH2_CHAR = ("Breath Rate 2","00002a3d-0000-1000-8000-00805f9b34fb", 28)
PRESSURE_CHAR = ("Intermediate Cuff Pressure", "00002a36-0000-1000-8000-00805f9b34fb", 31)
CONFIG_CHAR = ("Device Configuration", "b3ad0002-67ba-a4ea-2d8a-328fc521ab34", 34)
STREAM_CHAR = ("Live Stream","b3ad0003-67ba-a4ea-2d8a-328fc521ab34", 36)

CLIENT_CONFIG_DESC = ("Client Configuration", "00002902-0000-1000-8000-00805f9b34fb", 38)

# dictionary of characteristics that have to be read

READ_CHAR_DICT = {
    "HR_CHAR" : HR_CHAR,
    "TEMP_CHAR" : TEMP_CHAR,
    "BATTERY_CHAR" : BATTERY_CHAR
}

# MQTT

MQTT_BROKER = "localhost"
MQTT_PORT   = 1883
MQTT_TOPIC  = "unisadiem/dmcs/sensor/ACC_GYRO"

# Initial values for gesture classification

SENSOR_REST_X = -320
SENSOR_REST_Y = -32
SENSOR_REST_Z = 16768

# Number of samples for moving average 

SENSOR_SMOOTHING_WINDOW = 3

GESTURE_DEADZONE_X = 150
GESTURE_DEADZONE_Y = 150
GESTURE_THRESHOLD_LEFT  = -800
GESTURE_THRESHOLD_RIGHT =  800
GESTURE_THRESHOLD_FWD   =  500
GESTURE_THRESHOLD_BWD   = -500

GESTURE_JUMP_THRESHOLD_Z = 1200   
WINDOW_W = 1024
WINDOW_H = 720
FPS = 60
WINDOW_TITLE = "Howdy Senior — Avatar 3D"

# AVATAR

AVATAR_SPEED = 0.18   
JUMP_FORCE   = 0.22   
GRAVITY      = 0.010  
SCENE_BOUND  = 4.5    

# Camera

CAM_DISTANCE = 7.0    # distance avatar-camera
CAM_PITCH    = 25.0   # vertical angle 
CAM_ANGLE    = 30.0   # horizontal angle 
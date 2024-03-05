import random
import argparse
from typing import Final
import time
from paho.mqtt import client as mqtt_client
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010
from PIL import ImageFont

# Add command line arguments for setting config
parser = argparse.ArgumentParser()
parser.add_argument('-q', '--mqtt_host')
parser.add_argument('-u', '--mqtt_user')
parser.add_argument('-p', '--mqtt_password')
parser.add_argument('-l', '--mqtt_message_lisener')
parser.add_argument('-m', '--message')
parser.add_argument('-n', '--message_unit')
parser.add_argument('-f', '--message_font_size', type=int)
parser.add_argument('-s', '--message_unit_font_size', type=int)
parser.add_argument('-d', '--display_type')
parser.add_argument('-r', '--display_rotate', type=int)
parser.add_argument('-i', '--display_interface_serial')
parser.add_argument('-t', '--display_interface_port', type=int)
parser.add_argument('-a', '--display_interface_address', type=int)
args = parser.parse_args()

# Set config options
MQTT_HOST: Final = args.mqtt_host
MQTT_USER: Final = args.mqtt_user
MQTT_PASSWORD: Final = args.mqtt_password
MQTT_MESSAGE_LISENER: Final = args.mqtt_message_lisener
MESSAGE_UNIT: Final = args.message_unit
DISPLAY_TYPE: Final = args.display_type
DISPLAY_ROTATE: Final = args.display_rotate
DISPLAY_INTERFACE_SERIAL: Final = args.display_interface_serial
DISPLAY_INTERFACE_SERIAL_PORT: Final = args.display_interface_port
DISPLAY_INTERFACE_SERIAL_ADDRESS: Final = args.display_interface_address #0x3C
# Generate a Client ID with the subscribe prefix.
#client_id = f'subscribe-{random.randint(0, 100)}'

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_MESSAGE_LISENER)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload, encoding="UTF-8"))
    with canvas(device) as draw:
        #draw.rectangle(device.bounding_box, outline="white", fill="black")
        device.clear()
        if str(msg.payload, encoding="UTF-8") != "oled_off":
            device.show()
            draw.text((1, 1), str(msg.payload, encoding="UTF-8"), font=fnt, fill="white")
            draw.text((1, 41), MESSAGE_UNIT, font=fnt_unit, fill="white")
        else:
            device.hide()


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=MQTT_USER, password=MQTT_PASSWORD)
client.connect(MQTT_HOST, 1883, 60)



# Create the interface the device is connected to. Currently i2c support only.
interface = globals()[DISPLAY_INTERFACE_SERIAL](port=DISPLAY_INTERFACE_SERIAL_PORT, address=DISPLAY_INTERFACE_SERIAL_ADDRESS)
# Create the display device
device = globals()[DISPLAY_TYPE](interface, rotate=DISPLAY_ROTATE)
device.contrast(50)

fnt = ImageFont.truetype("/usr/bin/SF-Compact.ttf", size=args.message_font_size, encoding="unic")
fnt_unit = ImageFont.truetype("/usr/bin/SF-Compact.ttf", size=args.message_unit_font_size, encoding="unic")

# Draw some text
with canvas(device) as draw:
    # draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((1, 1), args.message, font=fnt, fill="white")

client.loop_forever()

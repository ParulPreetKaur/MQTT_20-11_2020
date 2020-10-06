from config import *
import paho.mqtt.client as mqtt
from vehicle_commands import *
import json
import time

class Vehicle:
    def __init__(self, name):
        self.name = name
        self.min_speed_mph = 0
        self.max_speed_mph = 10

    def print_action_with_name_prefix(self, action):
        print("{}: {}".format(self.name, action))

    def traffic_info(self):
        self.print_action_with_name_prefix("Traffic info at Downtown")

class VehicleCommandProcessor:
    commands_topic = ""
    processed_commands_topic = ""
    active_instance = None

    def __init__(self, name, vehicle):
        self.name = name
        self.vehicle = vehicle
        VehicleCommandProcessor.commands_topic = \
            "vehicles/{}/commands".format(self.name)
        VehicleCommandProcessor.processed_commands_topic = \
            "vehicles/{}/executedcommands".format(self.name)
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        VehicleCommandProcessor.active_instance = self
        self.client.on_connect = VehicleCommandProcessor.on_connect
        self.client.on_subscribe = VehicleCommandProcessor.on_subscribe
        self.client.on_message = VehicleCommandProcessor.on_message
        #self.client.tls_set(ca_certs = ca_certificate,
          #  certfile=client_certificate,
           # keyfile=client_key)

        self.client.connect (host=mqtt_server_host,port=mqtt_server_port,keepalive=mqtt_keepalive)

    def on_connect(client, userdata, flags, rc):
        print("Result from connect: {}".format(
            mqtt.connack_string(rc)))
        # Check whether the result form connect is the CONNACK_ACCEPTED  
        #connack code
        if rc == mqtt.CONNACK_ACCEPTED:
            # Subscribe to the commands topic filter
            client.subscribe(VehicleCommandProcessor.commands_topic, qos=2)

     #@staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("I've subscribed with QoS: {}".format(granted_qos[0]))

     #@staticmethod
    def on_message(client, userdata, msg):
        if msg.topic == VehicleCommandProcessor.commands_topic:
            print("Received message payload: {0}".format(str(msg.payload)))
            try:
                message_dictionary = json.loads(msg.payload)
                if COMMAND_KEY in message_dictionary:
                    command = message_dictionary[COMMAND_KEY]
                    vehicle = VehicleCommandProcessor.active_instance.vehicle
                    is_command_executed = False
                    if KEY_MPH in message_dictionary:
                        mph = message_dictionary[KEY_MPH]
                    else:
                        mph = 0
                    if KEY_DEGREES in message_dictionary:
                        degrees = message_dictionary[KEY_DEGREES]
                    else:
                        degrees = 0
                    command_methods_dictionary = {
                        #CMD_TURN_ON_ENGINE: lambda:
                        #vehicle.turn_on_engine(),
                        CMD_TRAFFIC_INFO: lambda:
                        vehicle.traffic_info(),
                        #CMD_TURN_OFF_ENGINE: lambda:
                        #vehicle.turn_off_engine(),
                        #CMD_LOCK_DOORS: lambda: vehicle.lock_doors(),
                        #CMD_UNLOCK_DOORS: lambda:
                        #vehicle.unlock_doors(),
                        #CMD_PARK: lambda: vehicle.park(),
                        #CMD_PARK_IN_SAFE_PLACE: lambda:
                        #vehicle.park_in_safe_place(),
                        #CMD_TURN_ON_HEADLIGHTS: lambda:
                        #vehicle.turn_on_headlights(),
                        #CMD_TURN_OFF_HEADLIGHTS: lambda:
                        #vehicle.turn_off_headlights(),
                        #CMD_TURN_ON_PARKING_LIGHTS: lambda:
                        #vehicle.turn_on_parking_lights(),
                        #CMD_TURN_OFF_PARKING_LIGHTS: lambda:
                        #vehicle.turn_off_parking_lights(),
                        #CMD_ACCELERATE: lambda: vehicle.accelerate(),
                        #CMD_BRAKE: lambda: vehicle.brake(),
                        #CMD_ROTATE_RIGHT: lambda:
                        #vehicle.rotate_right(degrees),
                        #CMD_ROTATE_LEFT: lambda:
                        #vehicle.rotate_left(degrees),
                        #CMD_SET_MIN_SPEED: lambda:
                        #vehicle.set_min_speed(mph),
                        #CMD_SET_MAX_SPEED: lambda:
                        #vehicle.set_max_speed(mph),
                    }
                    if command in command_methods_dictionary:
                        method = command_methods_dictionary[command]
                        # Call the method
                        method()
                        is_command_executed = True
                    if is_command_executed:
                        VehicleCommandProcessor.active_instance.publish_executed_command_message(message_dictionary)
                    else:
                        print("I've received a message with an unsupported command.")
            except ValueError:
                # msg is not a dictionary
                # No JSON object could be decoded
                print("I've received an invalid message.")

    def publish_executed_command_message (self, message):
         response_message = json.dumps({SUCCESFULLY_PROCESSED_COMMAND_KEY: message[COMMAND_KEY]})
         result = self.client.publish(topic = self.__class__.processed_commands_topic,payload = response_message)
         return result

    def process_incoming_commands(self):
        self.client.loop()


if __name__ == "__main__":
    vehicle = Vehicle("vehiclepi02")
    vehicle_command_processor = VehicleCommandProcessor("vehiclepi02", vehicle)
    while True:
        # Process messages and the commands every 1 second
        vehicle_command_processor.process_incoming_commands()
        time.sleep(1)
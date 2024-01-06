import paho.mqtt.client as mqtt
import time
from random import random, randint
import json

THINGSBOARD_HOST = "localhost"
DEVICE_ACCESS_TOKEN = "ZMRJndi1q2ElqHZMrt18"
TOPIC = "v1/devices/me/telemetry"

wait_time = 2
max_fuel = 5000
current_fuel = 4500
fuel_consumption = 5
current_fuel_percentage = (current_fuel / max_fuel) * 100

payload = {'max_fuel': max_fuel, 'current_fuel': current_fuel, 'fuel_consumption': fuel_consumption, 'current_fuel_percentage': current_fuel_percentage, 'distace_to_go': 0, 'going': False, 'out_of_fuel': False}
    
client = mqtt.Client()
client.username_pw_set(DEVICE_ACCESS_TOKEN, "")
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()
client.publish(TOPIC, json.dumps(payload))

print(f"You have a car that has {current_fuel}L out of {max_fuel}L of fuel, and a fuel consumption of {fuel_consumption} L/Km.")

try:
    while True:
        if (not payload["going"]):
            options = int(input("Options: (1: Go somewhere, 3: Fuel up, 4: Check fuel tank): "))
        else:
            options = int(input("Options: (1: Keep going, 2: Stop, 3: Fuel up, 4: Check fuel tank): "))

        match options: 
            case 1:
                if (not payload["out_of_fuel"]):
                    if (not payload["going"]):
                        distace = int(input("How far do you want to go (Km): "))
                        if (distace > 0):
                            payload["distace_to_go"] = distace
                            payload["going"] = True
                        else:
                            print("You can't go a negative distance!")
                    else:
                        if (payload["distace_to_go"] > 0):
                            if (payload["current_fuel"] < payload["fuel_consumption"]):
                                payload["distace_to_go"] = 0
                                payload["current_fuel"] = 0
                                payload["out_of_fuel"] = True
                                payload["going"] = False
                                print("You are out of fuel!")
                            else:
                                payload["distace_to_go"] -= 1
                                payload["current_fuel"] -= payload["fuel_consumption"]
                                print(f"You have {payload['distace_to_go']} km left.")
                        else:
                            payload["going"] = False
                            print("Yoe have arrived at your destination!")
                else:
                    print("You are out of fuel!")

                payload["current_fuel_percentage"] = (payload["current_fuel"] / payload["max_fuel"]) * 100
                time.sleep(wait_time)
                client.publish(TOPIC, json.dumps(payload))

            case 2:
                payload["distace_to_go"] = 0
                payload["going"] = False

                client.publish(TOPIC, json.dumps(payload))

            case 3:
                payload["current_fuel"] = payload["max_fuel"]
                payload["out_of_fuel"] = False
                print(f"You have fueled up! ({payload['max_fuel']})")
                payload["current_fuel_percentage"] = (payload["current_fuel"] / payload["max_fuel"]) * 100

                client.publish(TOPIC, json.dumps(payload))

            case 4:
                print(f"Fuel: ({payload['current_fuel']} / {payload['max_fuel']})")

except KeyboardInterrupt:
    pass

except ValueError:
    print("Invalid value given, program ends.")

client.loop_stop()
client.disconnect()
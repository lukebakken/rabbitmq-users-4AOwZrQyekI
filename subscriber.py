"""Subscribe to messages from RabbitMQ broker using MQTT"""

import argparse
import os
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, return_code):
    """The callback for when the client receives a CONNACK response from the server"""
    if return_code == 0:
        print("Connection successful")
        # Subscribe to the topic passed as an argument
        client.subscribe(userdata["topic"])
    else:
        print(f"Failed to connect, return code {return_code}\n")


def on_message(client, userdata, message):
    try:
        """The callback for when a PUBLISH message is received from the server"""
        payload = message.payload.decode()
        parts = payload.split(" | ")

        # Extract relevant parts from the message
        cluster = parts[0]
        client_id = parts[1]
        timestamp = parts[2]
        vhost = parts[3]
        index = int(parts[4])
        large_message = parts[5] if len(parts) > 5 else ""

        if index % 10 == 0:
            print(
                f"Message received from client '{client_id}' with index '{index}' and payload '{payload[:44]}...'"
            )  # Print only first 45 characters of payload
    except KeyboardInterrupt:
        print("[INFO] SUBSCRIBER EXITING")


def main():
    """Main method"""
    client = mqtt.Client(
        userdata={"topic": "rabbitmq-users-4AOwZrQyekI"}
    )  # Pass topic as userdata
    username = "guest"
    password = "guest"
    vhost = "/"
    node = "localhost"

    print(f"username: {username}, password: {password}, vhost: {vhost}")
    client.username_pw_set(username=f"{vhost}:{username}", password=password)

    print(f"Connecting to node [{node}]")

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(node, 1883, 60)

    client.loop_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] SUBSCRIBER EXITING")

"""Publish messages to RabbitMQ broker using MQTT"""

import argparse
import datetime
import time
import uuid
import multiprocessing
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, return_code):
    """The callback for when the client receives a CONNACK response from the server"""
    if return_code == 0:
        print("Connection successful")
    else:
        print(f"Failed to connect, return code {return_code}\n")


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p", "--publishers", help="Number of Publishers", type=int, default=1
    )
    args = parser.parse_args()
    return args


def publisher(node, topic, publisher_id):
    """Publisher function to run in each process"""
    message_prefix = f"This message was published to {node}"
    client_id = str(uuid.uuid4())
    client = mqtt.Client(client_id=client_id)

    username = "guest"
    password = "guest"
    vhost = "/"

    print(f"username: {username}, password: {password}, vhost: {vhost}")
    client.username_pw_set(username=f"{vhost}:{username}", password=password)

    print(f"Connecting to node [{node}] with clientID [{client_id}]")
    client.on_connect = on_connect
    client.connect(node, 1883, 60)
    large_message = "X" * 1000000  # Example large message (1 million characters)
    index = 0

    try:
        while True:
            client.loop(0.5)
            message = f"{message_prefix} | {client_id} | {time.time()} | {vhost} | {index} | {large_message}"
            if index % 100 == 0:
                print(
                    f'Publisher {publisher_id} with client_id "{client_id}" publishing message {index} at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")}'
                )
            client.publish(topic, message, 0, False)
            client.loop(0.5)
            index += 1
    except KeyboardInterrupt:
        print("[INFO] PUBLISHER EXITING!")


def main():
    """Main method"""
    args = parse_args()
    publishers = args.publishers
    topic = "rabbitmq-users-4AOwZrQyekI"
    node = "localhost"

    with multiprocessing.Pool(processes=publishers) as pool:
        try:
            pool.starmap(
                publisher,
                [(node, topic, i) for i in range(publishers)],
            )
        except KeyboardInterrupt:
            print("[INFO] EXITING!")


if __name__ == "__main__":
    main()

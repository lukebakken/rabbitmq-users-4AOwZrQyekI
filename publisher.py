"""Publish messages to RabbitMQ broker using MQTT"""

import argparse
import datetime
import os
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
    client.subscribe("HELLO")


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--cluster", help="Cluster", required=True)
    parser.add_argument("-n", "--node", help="Node Name", required=True)
    parser.add_argument("-t", "--topic", help="Topic Name", required=True)
    parser.add_argument(
        "-p", "--publishers", help="Number of Publishers", type=int, default=1
    )
    args = parser.parse_args()
    return args


def publisher(cluster, node, topic, publisher_id):
    """Publisher function to run in each process"""
    message_prefix = f"This message was published to {cluster} cluster"
    client_id = str(uuid.uuid4())
    client = mqtt.Client(client_id=client_id)
    username = os.getenv(f"{cluster.upper()}_USERNAME")
    password = os.getenv(f"{cluster.upper()}_PASSWORD")
    vhost = os.getenv(f"{cluster.upper()}_VHOST")
    print(f"username: {username}, password: {password}, vhost: {vhost}")
    client.username_pw_set(username=f"{vhost}:{username}", password=password)
    print(
        f"Connecting to [{cluster}] cluster on node [{node}] with clientID [{client_id}]"
    )
    client.on_connect = on_connect
    client.connect(node, 1883, 60)
    index = 0
    large_message = "X" * 1000000  # Example large message (1 million characters)

    while True:
        message = f"{message_prefix} | {client_id} | {time.time()} | {vhost} | {index} | {large_message}"
        print(
            f'Publisher {publisher_id} with client_id "{client_id}" publishing message at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")}'
        )
        client.publish(topic, message, 0, False)
        client.loop()
        time.sleep(0.1)
        index += 1


def main():
    """Main method"""
    args = parse_args()
    publishers = args.publishers

    with multiprocessing.Pool(publishers) as pool:
        pool.starmap(
            publisher,
            [(args.cluster, args.node, args.topic, i) for i in range(publishers)],
        )


if __name__ == "__main__":
    main()

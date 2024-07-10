"""Subscribe to messages from RabbitMQ broker using MQTT"""

import argparse
import os
import paho.mqtt.client as mqtt

# Dictionary to store the last received index for each publisher
last_received_index = {}


def on_connect(client, userdata, flags, return_code):
    """The callback for when the client receives a CONNACK response from the server"""
    if return_code == 0:
        print("Connection successful")
        # Subscribe to the topic passed as an argument
        client.subscribe(userdata["topic"])
    else:
        print(f"Failed to connect, return code {return_code}\n")


def on_message(client, userdata, message):
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

    # Use client_id as the unique identifier for the publisher
    publisher_id = client_id

    # Check if this is the first message from the publisher
    if publisher_id not in last_received_index:
        last_received_index[publisher_id] = index - 1

    # Verify the order of the messages
    if index == last_received_index[publisher_id] + 1:
        print(
            f"Message received in order from client '{publisher_id}' with index '{index}' and payload '{payload[:44]}...'"
        )  # Print only first 45 characters of payload
        last_received_index[publisher_id] = index
    else:
        print(
            f"Message OUT OF ORDER from client '{publisher_id}' with index '{index}' and payload '{payload[:45]}...' Expected index {last_received_index[publisher_id] + 1}"
        )
        last_received_index[publisher_id] = (
            index  # Update the index to the current index
        )


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--cluster", help="Cluster", required=True)
    parser.add_argument("-n", "--node", help="Node Name", required=True)
    parser.add_argument("-t", "--topic", help="Topic Name", required=True)
    args = parser.parse_args()
    return args


def main():
    """Main method"""
    args = parse_args()
    client = mqtt.Client(userdata={"topic": args.topic})  # Pass topic as userdata
    username = os.getenv(f"{args.cluster.upper()}_USERNAME")
    password = os.getenv(f"{args.cluster.upper()}_PASSWORD")
    vhost = os.getenv(f"{args.cluster.upper()}_VHOST")
    print(f"username: {username}, password: {password}, vhost: {vhost}")
    client.username_pw_set(username=f"{vhost}:{username}", password=password)
    print(f"Connecting to [{args.cluster}] cluster on node [{args.node}]")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(f"{args.node}", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()

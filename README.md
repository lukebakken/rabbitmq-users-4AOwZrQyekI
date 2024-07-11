# Setup

```
pipenv install
```

# Publisher

```
pipenv run python ./publisher.py --publishers=200
```

# Subscriber

```
pipenv run python ./subscriber.py
```

# Reproduction

Kill the subscriber with CTRL-C while running Observer or Observer CLI, with processes sorted by memory. You will see a `rabbit_mqtt_reader` process start to consume a _LOT_ of memory. It may take a couple of attempts.

If you run `publisher.py` with only a few publishers, you will see RabbitMQ log a large stack trace sometimes when hitting CTRL-C for a subscriber. This is due to the unhandled `exit`, which prints the message body and, in the case of 1MiB messages, can be a lot of output.

After applying https://github.com/rabbitmq/rabbitmq-server/pull/11676, these abrupt closures will always result in a clean shutdown of the reader process.

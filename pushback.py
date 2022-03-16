#!/usr/bin/env python3

import pika, pika.channel
from argparse import ArgumentParser
import logging
import os
import re
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(funcName)s [%(levelname)s] %(message)s')

logger = logging.getLogger(__name__)
logger.level = logging.INFO

filename_matcher = re.compile("([\w\d.]+)_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).json")


def process_file(path: str, filename: str):
    parts = filename_matcher.match(filename)
    if parts is None:
        logger.error("Could not match routing key and message id from {0}".format(filename))
        return
    routing_key = parts.group(1)
    message_id = parts.group(2)
    fullpath = os.path.join(path, filename)

    with open(fullpath, "rb") as f:
        content = f.read()

    logger.info("Key {0} id {1} content-length {2} filename {3}".format(routing_key, message_id, len(content), fullpath))

    if args.dry_run:
        logger.info("Not pushing messages, remove --dry-run to do this")
    else:
        logger.info("Pushing to {0} with roting key {1}".format(args.exchange, routing_key))
        props = pika.BasicProperties(content_type="application/json",content_encoding="UTF-8", message_id=message_id)
        channel.basic_publish(args.exchange, routing_key, content, props)


if __name__ == "__main__":
    parser = ArgumentParser(description="Take a directory of dumped json files and push them onto a queue as messages")
    parser.add_argument("--host", type=str, help="RabbitMQ host")
    parser.add_argument("--port", type=int, help="RabbitMQ port", default=5672)
    parser.add_argument("--vhost", type=str, help="Vhost to connect to RabbitMQ with", default="/")
    parser.add_argument("--user", type=str, help="Username for rabbitmq")
    parser.add_argument("--passwd", type=str, help="Password for rabbitmq")
    parser.add_argument("--exchange", type=str, help="Exchange name to publish to")
    parser.add_argument("--path", type=str, help="Path to read message JSON files from", default=os.getcwd())
    parser.add_argument("--dry-run", action='store_true', help="Show what would be done, don't push onto the queue")

    args = parser.parse_args()

    conn = pika.BlockingConnection(pika.ConnectionParameters(host=args.host,
                                                             virtual_host=args.vhost,
                                                             credentials=pika.PlainCredentials(args.user, args.passwd)))

    channel = conn.channel()

    with os.scandir(args.path) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file() and entry.name.endswith(".json"):
                process_file(args.path, entry.name)
            else:
                logger.debug("Ignoring {0}".format(entry.name))
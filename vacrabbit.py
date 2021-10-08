#!/usr/bin/env python3

import pika, pika.channel
from argparse import ArgumentParser
import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(funcName)s [%(levelname)s] %(message)s')

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_filename(method:pika.spec.Basic.Deliver, properties:pika.spec.BasicProperties) -> str:
    if properties.message_id is not None:
        return method.routing_key + "_" + properties.message_id + ".json"
    else:
        return method.routing_key + "_" + str(method.delivery_tag) + ".json"


def received(ch:pika.channel.Channel, method:pika.spec.Basic.Deliver, properties:pika.spec.BasicProperties, body:bytes):
    filename = get_filename(method, properties)
    logger.info("Writing message with id {0} from exchange {1} with delivery tag {2} to {3}".format(properties.message_id, method.exchange, method.delivery_tag, filename))
    with open(filename, "wb") as f:
        f.write(body)
    ch.basic_nack(method.delivery_tag, requeue=True)


if __name__ == "__main__":
    parser = ArgumentParser(description="Suck the contents of a rabbitMQ (dead-letter) queue onto disk")
    parser.add_argument("--host", type=str, help="RabbitMQ host")
    parser.add_argument("--port", type=int, help="RabbitMQ port", default=5672)
    parser.add_argument("--vhost", type=str, help="Vhost to connect to RabbitMQ with", default="/")
    parser.add_argument("--user", type=str, help="Username for rabbitmq")
    parser.add_argument("--passwd", type=str, help="Password for rabbitmq")
    parser.add_argument("--queue", type=str, help="Queue name to pull")
    parser.add_argument("--requeue", action='store_true', help="Put the messages back on the queue after we read them")

    args = parser.parse_args()

    conn = pika.BlockingConnection(pika.ConnectionParameters(host=args.host,
                                                             virtual_host=args.vhost,
                                                             credentials=pika.PlainCredentials(args.user, args.passwd)))

    logger.info("Starting up, press CTRL-C when you have captured all the messages you want")
    channel = conn.channel()
    channel.basic_consume(queue=args.queue,on_message_callback=received)
    channel.start_consuming()

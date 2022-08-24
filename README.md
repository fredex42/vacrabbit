# vacrabbit

## What is it?

This is a couple of scripts to help when dealing with dead-letter queues in RabbitMQ.  They allow you to
"vacuum" the entire contents of a queue out to individual files on-disk, optionally deleting it as you go, and
to "pushback" files on-disk to an exchange.

This means that you can extract the whole queue, separate out any problematic messages, requeue the rest, etc.

## How do I use it?

Option 1 - use the Docker image that is built by Github.  This is available from the "Releases" page.
Option 2 - just clone the repository, run `pip3 install -r requirements.txt` and run the scripts directly.

### vacrabbit

```
usage: vacrabbit.py [-h] [--host HOST] [--port PORT] [--vhost VHOST] [--user USER] [--passwd PASSWD] [--queue QUEUE] [--requeue]

Suck the contents of a rabbitMQ (dead-letter) queue onto disk

optional arguments:
-h, --help       show this help message and exit
--host HOST      RabbitMQ host
--port PORT      RabbitMQ port
--vhost VHOST    Vhost to connect to RabbitMQ with
--user USER      Username for rabbitmq
--passwd PASSWD  Password for rabbitmq
--queue QUEUE    Queue name to pull
--requeue        Put the messages back on the queue after we read them
```

If you want to pull the contents of the queue called `myapp-deadletter` into the `suspect-messages/` directory, here is
how you would do it:
```bash
mkdir suspect-messages/
cd suspect-messages/
../vacrabbit.py --host {my-rabbitmq} --vhost {vhost-name-or-/} --user {rmq-user} --passwd {rmq-passwd} --queue myapp-deadletter
```

Once all messages have been retrieved, you will need to **manually cancel execution via CTRL-C**.

You should see the messages removed from the queue and a lot of json files in the `suspect-messages` directory. You can
then analyse them at will.

### pushback

```
usage: pushback.py [-h] [--host HOST] [--port PORT] [--vhost VHOST] [--user USER] [--passwd PASSWD] [--exchange EXCHANGE] [--path PATH] [--dry-run]

Take a directory of dumped json files and push them onto a queue as messages

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          RabbitMQ host
  --port PORT          RabbitMQ port
  --vhost VHOST        Vhost to connect to RabbitMQ with
  --user USER          Username for rabbitmq
  --passwd PASSWD      Password for rabbitmq
  --exchange EXCHANGE  Exchange name to publish to
  --path PATH          Path to read message JSON files from
  --dry-run            Show what would be done, don't push onto the queue
```


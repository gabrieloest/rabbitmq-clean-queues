import pika
import os
import logging
import config_resolver
import rabbitmq_api_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = config_resolver.ConfigResolver(logger)
server_config = config.load_server_config()

logger.info("Parse URL...")
url = os.environ.get('URL', 'amqp://{}:{}@{}/{}'
                     .format(server_config['user'], server_config['password'],
                             server_config['host'], server_config['vhost']))

params = pika.URLParameters(url)
params.socket_timeout = 5

logger.info("Connect to server...")
connection = pika.BlockingConnection(params)
channel = connection.channel()

rmq_utils = rabbitmq_api_utils.RabbitmqAPIUtils(server_config['host'],
                                                server_config['user'],
                                                server_config['password'])

policies_config = config.load_policies_config()

all_queues = rmq_utils.get_all_queues()

queues_to_clean = list(filter(
    lambda item: (item['consumers'] == 0 and
                  policies_config['dead-letter-routing-key'] not in item["name"]),
    all_queues.json()))

queues_names = list(map(lambda item: item['name'], queues_to_clean))

logger.info("Queues found: ")
logger.info(queues_names)

queue_name_vhost = dict((json["name"], json["vhost"])
                        for json in queues_to_clean)
logger.info(queue_name_vhost)
queue_name_vhost = {
    k: v for (k, v) in queue_name_vhost.items() if k in queues_names}

for key in queue_name_vhost:
    logger.info(key)
    dead_letter_exchange = "{}.{}".format(policies_config['dead-letter-exchange'], queue_name_vhost.get(key))

    if not rmq_utils.is_exchange_exists(queue_name_vhost.get(key), dead_letter_exchange):
        logger.info('Dead leter exchange does not exist in the vhost {}. '
                    'Creating...'.format(queue_name_vhost.get(key)))
        rmq_utils.create_exchange(
            queue_name_vhost.get(key), dead_letter_exchange)


class CountCallback(object):
    def __init__(self, count, exchange, routing_key):
        self.count = count
        self.exchange = exchange
        self.routing_key = routing_key

    def __call__(self, channel, method, properties, body):
        logger.info("Message processed count {}".format(self.count))
        logger.info("Republish message to {}".format(self.routing_key))
        channel.basic_publish(
            exchange='', routing_key=self.routing_key, body=body)

        self.count -= 1
        if not self.count:
            channel.stop_consuming()


for key, value in queue_name_vhost.items():
    dead_letter_exchange = "{}.{}".format(policies_config['dead-letter-exchange'], value)
    dead_letter_queue = "{}.{}".format(policies_config['dead-letter-routing-key'], key)

    exists_queue = rmq_utils.is_queue_exists(value, dead_letter_queue)
    if not exists_queue:
        logger.info("Create Dead Letter Queue {}....".format(
            dead_letter_queue))
        queue_response = rmq_utils.create_queue(value, dead_letter_queue)
        logger.info("Queue code: {}".format(queue_response))
        rmq_utils.create_binding(
            value, dead_letter_exchange, dead_letter_queue)

        logger.info(
            "Set Messages TTL and Dead Letter Exchange policies for the queue"
            "{} in vhost {}...".format(key, value))
        policy_response = rmq_utils.create_queue_policy(
            value, key, policies_config)
        logger.info("Policy code: {}".format(policy_response))

    print('Processing queue {}'.format(key))
    queue = channel.queue_declare(key)
    message_count = queue.method.message_count
    logger.info("Check message count... total: {}".format(message_count))
    if(message_count > 0):
        logger.info("create CountCallback")
        callback = CountCallback(queue.method.message_count,
                                 dead_letter_exchange, dead_letter_queue)
        channel.basic_consume(callback, queue=key, no_ack=True)
        channel.start_consuming()

    logger.info("Done!")

channel.close()
connection.close()

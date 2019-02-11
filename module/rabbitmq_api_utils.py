import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitmqAPIUtils:

    headers = {'Content-type': 'application/json'}

    def __init__(self, protocol, host, user, password):
        self.user = user
        self.password = password
        self.url = '{}://{}/api/'.format(protocol, host)

    def get_all_queues(self):
        logger.info("Call RabbitMQ api... {}".format(self.url))
        url_method = self.url
        url_method += 'queues'
        r = requests.get(url_method, auth=(self.user, self.password))
        return r

    def create_queue(self, vhost, queue):
        logger.info("Call RabbitMQ api...")
        url_method = self.url
        url_method += ('queues/{}/{}'.format(vhost, queue))
        logger.info("Create Queue URL: {}".format(url_method))
        data = {"auto_delete": False, "durable": True}
        logger.info("Create Queue DATA: {}".format(data))
        r = requests.put(url_method, auth=(self.user, self.password),
                         data=json.dumps(data), headers=self.headers)
        return r

    def is_queue_exists(self, vhost, queue):
        logger.info("Call RabbitMQ api...")
        logger.info("Verifying if queue {} exists...".format(queue))
        url_method = self.url
        url_method += ('queues/{}/{}'.format(vhost, queue))
        r = requests.get(url_method, auth=(self.user, self.password))
        return r.status_code == 200

    def is_exchange_exists(self, vhost, exchange):
        logger.info("Call RabbitMQ api...")
        logger.info("Verifying if exchange {} exists...".format(exchange))
        url_method = self.url
        url_method += ('exchanges/{}/{}'.format(vhost, exchange))
        r = requests.get(url_method, auth=(self.user, self.password))
        return r.status_code == 200

    def create_exchange(self, vhost, exchange):
        logger.info("Call RabbitMQ api...")
        url_method = self.url
        url_method += ('exchanges/{}/{}'.format(vhost, exchange))
        logger.info("Create Exchange URL: {}".format(url_method))
        headers = {'Content-type': 'application/json'}
        data = {"type": "direct", "auto_delete": False, "durable": True}
        logger.info("Create Exchange DATA: {}".format(data))
        r = requests.put(url_method, auth=(self.user, self.password),
                         data=json.dumps(data), headers=headers)
        return r

    def create_binding(self, vhost, exchange, queue):
        logger.info("Call RabbitMQ api...")
        url_method = self.url
        url_method += ('bindings/{}/e/{}/q/{}'.format(vhost, exchange, queue))
        logger.info("Create Binding URL: {}".format(url_method))
        headers = {'Content-type': 'application/json'}
        data = {"routing_key": queue}
        logger.info("Create Binding DATA: {}".format(data))
        r = requests.post(url_method, auth=(
            self.user, self.password), data=json.dumps(data), headers=headers)
        return r

    def create_queue_policy(self, vhost, queue, policies_config):
        logger.info("Call RabbitMQ api...")

        dead_letter_exchange = "{}.{}".format(policies_config['dead-letter-exchange'], vhost)
        dead_letter_queue = "{}.{}".format(policies_config['dead-letter-routing-key'], queue)

        url_method = self.url
        url_method += ('policies/{}/default-policy-{}'.format(vhost, queue))
        logger.info("Set queue policy URL: {}".format(url_method))
        headers = {'Content-type': 'application/json'}
        data = {"pattern": "(^{})".format(queue),
                "definition": {"message-ttl": policies_config["message-ttl"],
                               "dead-letter-exchange": dead_letter_exchange,
                               "dead-letter-routing-key": dead_letter_queue,
                               "max-length": policies_config["max-length"],
                               "expires": policies_config["expires"],
                               "ha-mode": policies_config["ha-mode"],
                               "ha-sync-mode": policies_config["ha-sync-mode"]},
                "priority": 10, "apply-to": "queues"}
        logger.info("Set queue policy DATA: {}".format(data))
        r = requests.put(url_method, auth=(self.user, self.password),
                         data=json.dumps(data), headers=headers)
        return r

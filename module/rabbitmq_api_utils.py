import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitmqAPIUtils:

    headers = {'Content-type': 'application/json'}

    def __init__(self, host, user, password):
        self.user = user
        self.password = password
        self.url = 'https://{}/api/'.format(host)

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

    def create_queue_policy(self, vhost, queue, dlx, dlq):
        logger.info("Call RabbitMQ api...")
        url_method = self.url
        url_method += ('policies/{}/expiry-policy-{}'.format(vhost, queue))
        logger.info("Set queue policy URL: {}".format(url_method))
        headers = {'Content-type': 'application/json'}
        data = {"pattern": "(^{})".format(queue),
                "definition": {"message-ttl": 6000,
                               "ha-mode": "all",
                               "ha-sync-mode": "automatic",
                               "dead-letter-exchange": dlx,
                               "dead-letter-routing-key": dlq},
                "priority": 10, "apply-to": "queues"}
        logger.info("Set queue policy DATA: {}".format(data))
        r = requests.put(url_method, auth=(self.user, self.password),
                         data=json.dumps(data), headers=headers)
        return r

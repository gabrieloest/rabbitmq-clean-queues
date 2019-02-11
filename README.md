
# RabbitMQ Clean Queues

## About the project
The objective of this project is, given a RabbitMQ broker, read the queues and clean up the required ones. In addition, apply policies, so that the current situation is not repeated.
The cleaning of queues can be done with two different scripts:
  * clean_all_queues_basic_consume.py - In this script, the messages are read and transferred to the dead letter queues. In this way, if it is necessary that the messages are retrieved, they can be read "dead letter queues".
  * clean_all_queues_purge.py - Unlike the previous script, in this script, the messages are deleted. we use the "purge" method, so it is not possible to retrieve the messages in the future.

## How it works?
1. Read all queues
2. Filter queues that need a clean up
3. Create Dead Letter Exchange for each vhost
4. For each filtered queue
	1. Create Dead Letter Queue
	2. Bind the Dead Letter Queue with Dead Letter Exchange
	3. Apply the "Default Policies" in the queue
	4. Clean (Read and transfer to the "dead letter queues" or purge)

## Default Policies
The aim of the default policies, is to ensure that all the environments created, follow the best practices recognized for using RabbitMQ as a message broker. This policies will be set with a low priority, so they can be easily replaced.

### message-ttl
**Description**: Message TTL can be set for a given queue by setting the message-ttl argument with a policy or by specifying the same argument at the time of queue declaration.

A message that has been in the queue for longer than the configured TTL is said to be dead. Note that a message routed to multiple queues can die at different times, or not at all, in each queue in which it resides. The death of a message in one queue has no impact on the life of the same message in other queues.

The server guarantees that dead messages will not be delivered using basic.deliver (to a consumer) or included into a basic.get-ok response (for one-off fetch operations). Further, the server will try to remove messages at or shortly after their TTL-based expiry.

The value of the TTL argument or policy must be a non-negative integer (0 <= n), describing the TTL period in milliseconds. Thus a value of 1000 means that a message added to the queue will live in the queue for 1 second or until it is delivered to a consumer. The argument can be of AMQP 0-9-1 type short-short-int, short-int, long-int, or long-long-int.

**Value**: 60000 (1 minute)

### dead-letter-exchange
**Description**: Messages from a queue can be "dead-lettered"; that is, republished to an exchange when any of the following events occur:

- The message is negatively acknowledged by a consumer using basic.reject or basic.nack with requeue parameter set to false
- The message expires due to TTL; or
- The message is dropped because its queue exceeded a length limit

Dead letter exchanges (DLXs) are normal exchanges. They can be any of the usual types and are declared as usual.

**Value**: deadletter.{vhost name}

### dead-letter-routing-key
**Description**: Dead-lettered messages are routed to their dead letter exchange either:

- with the routing key specified for the queue they were on;
- with the same routing keys they were originally published with.

For example, if you publish a message to an exchange with routing key foo, and that message is dead-lettered, it will be published to its dead letter exchange with routing key foo. If the queue the message originally landed on had been declared with x-dead-letter-routing-key set to bar, then the message will be published to its dead letter exchange with routing key bar.

**Value**: deadletter.{queue name}

### max-length
**Description**: The maximum length of a queue can be limited to a set number of messages, or a set number of bytes (the total of all message body lengths, ignoring message properties and any overheads), or both.

The default behaviour for RabbitMQ when a maximum queue length or size is set and the maximum is reached is to drop or dead-letter messages from the front of the queue (i.e. the oldest messages in the queue).

**Value**: 50

### expires
**Description**: TTL can also be set on queues, not just queue contents. Queues will expire after a period of time only when they are not used (e.g. do not have consumers). This feature can be used together with the auto-delete queue property.

Expiry time can be set for a given queue by setting the x-expires argument to queue.declare, or by setting the expires policy. This controls for how long a queue can be unused before it is automatically deleted. Unused means the queue has no consumers, the queue has not been redeclared, and basic.get has not been invoked for a duration of at least the expiration period. This can be used, for example, for RPC-style reply queues, where many queues can be created which may never be drained.

**Value**: 2419200000(28 days)

### ha-mode
**Description**: By default, contents of a queue within a RabbitMQ cluster are located on a single node (the node on which the queue was declared). This is in contrast to exchanges and bindings, which can always be considered to be on all nodes. Queues can optionally be made mirrored across multiple nodes.

Each mirrored queue consists of one master and one or more mirrors. The master is hosted on one node commonly referred as the master node. Each queue has its own master node. All operations for a given queue are first applied on the queue's master node and then propagated to mirrors. This involves enqueueing publishes, delivering messages to consumers, tracking acknowledgements from consumers and so on.

all - Queue is mirrored across all nodes in the cluster. When a new node is added to the cluster, the queue will be mirrored to that node.

This setting is very conservative. Mirroring to a quorum (N/2 + 1) of cluster nodes is recommended instead. Mirroring to all nodes will put additional strain on all cluster nodes, including network I/O, disk I/O and disk space usage.

**Value**: all

### ha-sync-mode
**Descritption**: While a queue is being synchronised, all other queue operations will be blocked. Depending on multiple factors, a queue might be blocked by synchronisation for many minutes or hours, and in extreme cases even days.

automatic - a queue will automatically synchronise when a new mirror joins. It is worth reiterating that queue synchronisation is a blocking operation. If queues are small, or you have a fast network between RabbitMQ nodes and the ha-sync-batch-size was optimised, this is a good choice.

**Value**: automatic

## Configuration
1. Create file `config/server-config.yml` with the following content:
```
rabbitmq:
  protocol:
  host:
  user:
  password:
  vhost:
```
2. Fill the fields with the values to access your RabbitmMQ server
3. The default policies configuration file `config/policies-config.yml`, is filled with default values, but you can change it to adapt to your reality.
```
policies:
    message-ttl: 60000 #1 minute
    dead-letter-exchange: deadletter
    dead-letter-routing-key: deadletter
    max-length: 50
    expires: 2419200000 #28 days
    ha-mode: all
    ha-sync-mode: automatic

```

## Usage
```
git clone https://github.com/gabrieloest/rabbitmq-clean-queues
```
```
cd rabbitmq-clean-queues
```
```
python -m pip install -r requirements.txt
```
### To run the script to clean queues reading and transfering all messages to dead letter queues:
```
python module/clean_all_queues_basic_consume.py
```
### To run the script to clean queues deleting all the messages:
```
python module/clean_all_queues_purge.py
```
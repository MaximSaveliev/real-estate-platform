import pika
import json
from config.settings import get_settings

settings = get_settings()

class EventProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Connect to RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange='user_events',
            exchange_type='topic',
            durable=True
        )
        
    def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            self.connection.close()
            
    def publish_user_created(self, user_data):
        """Publish user created event"""
        if not self.channel:
            self.connect()
            
        self.channel.basic_publish(
            exchange='user_events',
            routing_key='user.created',
            body=json.dumps(user_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
    def publish_user_updated(self, user_data):
        """Publish user updated event"""
        if not self.channel:
            self.connect()
            
        self.channel.basic_publish(
            exchange='user_events',
            routing_key='user.updated',
            body=json.dumps(user_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

# Create global producer instance
event_producer = EventProducer()
import aio_pika
from config.settings import get_settings

settings = get_settings()

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("email-verification")
        await self.channel.declare_queue("notifications")

    async def publish(self, queue: str, message: str):
        if not self.channel:
            await self.connect()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue
        )

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
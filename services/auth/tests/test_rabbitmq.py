import asyncio
import aio_pika
from aio_pika import connect_robust

async def test_rabbitmq_connection():
    try:
        connection = await connect_robust(
            host="127.0.0.1",
            port=5672,
            login="guest",
            password="guest"
        )
        
        print("Successfully connected to RabbitMQ!")
        
        await connection.close()
        return True
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        return False

# Run the async function
if __name__ == "__main__":
    result = asyncio.run(test_rabbitmq_connection())
    exit(0 if result else 1)
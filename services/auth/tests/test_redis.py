import redis.asyncio as redis
import asyncio

async def test_redis_connection():
    client = redis.Redis(host="127.0.0.1", port=6379, db=0)
    try:
        result = await client.ping()
        if result:
            print("Successfully connected to Redis!")
            return True
        else:
            print("Failed to connect to Redis - ping returned false")
            return False
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return False
    finally:
        await client.aclose()

if __name__ == "__main__":
    result = asyncio.run(test_redis_connection())
    exit(0 if result else 1)
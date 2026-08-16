# test_redis_connection.py

import redis
from config import config

try:
    # Connect to Redis
    r = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
    
    # Ping Redis
    response = r.ping()
    
    if response:
        print("✅ Redis Connection Successful!")
        print(f"✅ URL: {config.REDIS_URL}")
        
        # Test set/get
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✅ Test set/get: {value}")
        
        # Clean up
        r.delete("test_key")
        print("✅ Connection verified and working!")
    else:
        print("❌ Redis ping failed")
        
except Exception as e:
    print(f"❌ Redis Connection Failed: {e}")
    print("Make sure Redis is running: redis-server (or redis-cli ping to verify)")
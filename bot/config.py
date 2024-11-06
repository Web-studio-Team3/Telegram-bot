import redis

redis_db = redis.StrictRedis(
    host='0.0.0.0',
    port=6379,
    password='qwerty',
    charset="utf-8",
    decode_responses=True
)
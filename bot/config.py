import redis

redis_db = redis.StrictRedis(
    host='redis',
    port=6379,
    password='',
    charset="utf-8",
    decode_responses=True,
    db=0
)

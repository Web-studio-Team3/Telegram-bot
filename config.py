import redis
from bestconfig import Config

# Доступ к переменным среды
conf = Config('.env')


# Подключение к Redis
redis_db = redis.StrictRedis(
    host='redis',
    port=6379,
    password='',
    charset="utf-8",
    decode_responses=True,
    db=0
)

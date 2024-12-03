import redis
from bestconfig import Config
from pymongo import MongoClient

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

mongo_db = MongoClient('mongodb://host.docker.internal:27017').baraholka
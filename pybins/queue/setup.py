import os
from rq import Queue
from redis import Redis

# Set up Redis connection and RQ queue
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(redis_url)
queue = Queue('builds', connection=redis_conn)

from .services import DepositsSchedulers
from celery import shared_task
from django.contrib.auth.models import User


#
# deposits_job = DepositsSchedulers()
# @shared_task()
# def make_deposits_capitalization():
#     add_job(deposits_job.add_deposits_capitalization,
#                    trigger='cron',
#                    hour=00,
#                    minute=1
#                    )


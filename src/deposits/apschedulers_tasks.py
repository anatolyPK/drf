from config.apscheduler_client import schedulers
from .services import DepositsSchedulers


print('APS DEP')
deposits_job = DepositsSchedulers()
schedulers.add_job(deposits_job.add_deposits_capitalization,
                   trigger='cron',
                   hour=00,
                   minute=1
                   )

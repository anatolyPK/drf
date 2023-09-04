from config.apscheduler_client import schedulers
from .services.refresh_bonds_shares_etfs_bd import TinkoffAssets


print('APS stocks')
schedulers.add_job(TinkoffAssets.update_all_shares,
                   trigger='cron',
                   hour=8,
                   minute=4
                   )


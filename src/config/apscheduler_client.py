from apscheduler.schedulers.background import BackgroundScheduler


schedulers = BackgroundScheduler()
schedulers.configure(timezone='Asia/Vladivostok')
schedulers.start()

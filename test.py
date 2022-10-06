import schedule
import time
from main import backup
if __name__=="__main__":
    schedule.every(5).seconds.do(backup)
    # schedule.every().day.at("13:00").do(backup)
    while True:
        schedule.run_pending()
        time.sleep(1)
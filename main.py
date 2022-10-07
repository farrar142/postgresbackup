import gzip
import os
import subprocess
import schedule
import time
import shutil
import dotenv
import io
from MyClient import S3File, s3_client
from pprint import pprint
from datetime import datetime
dotenv.load_dotenv()

BACKUP_DIR = "/root/backups"

ARCHIVE_DIRS = os.getenv("archives","archives")
DB_HOST=os.getenv("DB_HOST","172.17.0.1")
DB_USER=os.getenv('DB_USER',"user")
DB_PASSWORD=os.getenv("DB_PASSWORD",'password')
DB_PORT=os.getenv("DB_PORT","5432")
DB_NAME=os.getenv("DB_NAME",'dbname')
TIME=os.getenv("TIME",'03:00')

class File:
    def __init__(self, dir: str, file: str):
        self.origin = dir
        self.dir = dir
        self.file = file
        
    @classmethod
    def append_from_file_array(cls,dir:str,array:list[str]):
        file_name = array[0]
        array.remove(array[0])
        return cls(dir,file_name)

    @property
    def full(self):
        return f"{self.dir}/{self.file}"

    def remove(self):
        os.remove(self.full)

    def change_dir(self, dir: str):
        shutil.move(self.full, f"{dir}/{self.file}")
        self.dir = dir

    def get_date(self):
        _time = datetime.fromisoformat(self.file.split("_")[0])
        return f"{_time.year}-{_time.month}"
    
    def transfer_to_s3(self,dir:str):
        with open(self.full,'rb') as f:
            s3file = s3_client.upload(f,f"{dir}/{self.file}")
            return s3file


class Dir:
    def __init__(self):
        files = s3_client.get_files(ARCHIVE_DIRS)
        self.dict: dict[str, S3File] = {}
        for file in files:
            file_time = file.get_date()
            if self.dict.get(file_time):
                self.dict[file_time].remove()
            self.dict[file_time] = file

    def push(self, file: S3File):
        out_dated = self.dict.get(file.get_date())
        if out_dated:
            out_dated.remove()
        self.update(file)

    def update(self, file: S3File):
        self.dict[file.get_date()] = file


def check_backups():
    files = os.listdir(BACKUP_DIR)
    dir = Dir()
    while len(files) > 10:
        file = File.append_from_file_array(BACKUP_DIR,files)
        s3file = file.transfer_to_s3(ARCHIVE_DIRS)
        file.remove()
        dir.push(s3file)


def backup():
    cmd = f"PGPASSWORD={DB_PASSWORD} pg_dump --host={DB_HOST} --port {DB_PORT} -U {DB_USER} {DB_NAME} > ~/backups/{datetime.now().isoformat()}_backup.sql"
    subprocess.Popen(
            cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    check_backups()


if __name__=="__main__":
    # schedule.every(5).seconds.do(backup)
    schedule.every().day.at(TIME).do(backup)
    while True:
        schedule.run_pending()
        time.sleep(1)

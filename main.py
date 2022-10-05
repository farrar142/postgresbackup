import gzip
import os
import subprocess
import schedule
import time
import shutil
from pprint import pprint
from datetime import datetime
BACKUP_DIR = "/root/backups"
ARCHIVE_DIR = "/root/archives"


class File:
    def __init__(self, dir: str, file: str):
        self.origin = dir
        self.dir = dir
        self.file = file

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


class Dir():
    def __init__(self, dir: str):
        self.dir = dir
        files = os.listdir(dir)
        self.dict: dict[str, File] = {}
        for _file in files:
            file = File(ARCHIVE_DIR, _file)
            file_time = file.get_date()
            if self.dict.get(file_time):
                self.dict[file_time].remove()
            self.dict[file_time] = file

    def push(self, file: File):
        out_dated = self.dict.get(file.get_date())
        if out_dated:
            out_dated.remove()
        self.update(file)

    def update(self, file: File):
        file.change_dir(self.dir)
        self.dict[file.get_date()] = file


def check_backups():
    files = os.listdir(BACKUP_DIR)
    dir = Dir(ARCHIVE_DIR)
    while len(files) > 10:
        file = File(BACKUP_DIR, files[0])
        files.remove(files[0])
        dir.push(file)


def backup():
    cmd = f"pg_dump --host=172.17.0.1 --port 5432 -U runthe runthe > ~/backups/{datetime.now().isoformat()}_backup.sql"
    with gzip.open(f"backup.gz", 'wb') as f:
        popen = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        if popen.stdout:
            for stdout_line in iter(popen.stdout.readline, ""):
                f.write(stdout_line.encode("utf-8"))

            popen.stdout.close()
            popen.wait()
    check_backups()
    print("backup!")


# schedule.every(5).seconds.do(backup)
schedule.every().day.at("13:00").do(backup)
while True:
    schedule.run_pending()
    time.sleep(1)

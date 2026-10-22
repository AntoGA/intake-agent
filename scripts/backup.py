"""Запуск: python scripts/backup.py /absolute/path/intake.db /absolute/path/copy.db"""
import os,sqlite3,sys
from pathlib import Path
src,dst=map(Path,sys.argv[1:])
if not src.is_file():raise SystemExit('Исходная база не найдена')
fd=os.open(dst,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
a=sqlite3.connect(src.resolve().as_uri()+'?mode=ro',uri=True);b=sqlite3.connect(dst)
try:a.backup(b)
finally:a.close();b.close()
print('Резервная копия создана')

"""Создать .env с новыми токенами. Существующий файл не изменяется."""
import os,secrets
from pathlib import Path
root=Path(__file__).resolve().parents[1]
content=(root/'.env.example').read_text().replace('ADMIN_TOKEN=','ADMIN_TOKEN='+secrets.token_urlsafe(40)).replace('INGEST_TOKEN=','INGEST_TOKEN='+secrets.token_urlsafe(40))
fd=os.open(root/'.env',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:f.write(content)
print('.env создан. Токены не выводятся. Заполните настройки источников на сервере.')

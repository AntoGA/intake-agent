import email, imaplib, json, os, time
from email import policy
from email.utils import parseaddr
from urllib.request import urlopen
from core import ingest, cursor, process_one

def telegram_update(update):
    msg=update.get('message')
    if not msg or msg.get('chat',{}).get('type')!='private': return
    text=msg.get('text') or msg.get('caption') or '[Нет текста: вложение требует ручного просмотра в Telegram]'
    ingest('telegram',str(update['update_id']), 'telegram:'+str(msg['chat']['id']),text)

def telegram_poll():
    token=os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:return
    # getUpdates is used only after each previous update has been saved.
    with urlopen('https://api.telegram.org/bot'+token+'/getUpdates?timeout=0&offset='+cursor('telegram'),timeout=20) as r:
        data=json.load(r)
    if not data.get('ok'):raise RuntimeError('telegram error')
    for update in data['result']:
        telegram_update(update)
        cursor('telegram',update['update_id']+1)

def email_message(raw, identity):
    msg=email.message_from_bytes(raw,policy=policy.default)
    part=msg.get_body(preferencelist=('plain',))
    text=part.get_content() if part else '[Нет текстовой части: проверьте оригинал письма]'
    if any(msg.iter_attachments()):text+='\n[Вложения доступны только в оригинале письма]'
    return ingest('email',identity,parseaddr(str(msg.get('From','')))[1],(str(msg.get('Subject',''))+'\n'+str(text))[:20000])

def email_poll():
    host=os.getenv('IMAP_HOST')
    if not host:return
    folder=os.getenv('IMAP_FOLDER','INBOX')
    with imaplib.IMAP4_SSL(host,timeout=20) as m:
        m.login(os.environ['IMAP_USER'],os.environ['IMAP_PASSWORD'])
        typ,_=m.select(folder,readonly=True)
        if typ!='OK':raise RuntimeError('mailbox unavailable')
        validity=m.response('UIDVALIDITY')[1][0].decode()
        key='imap:'+host+':'+os.environ['IMAP_USER']+':'+folder+':'+validity
        last=int(cursor(key)); typ,data=m.uid('search',None,'UID',str(last+1)+':*')
        if typ!='OK':raise RuntimeError('search failed')
        for uid in data[0].split():
            if int(uid)<=last:continue
            typ,items=m.uid('fetch',uid,'(BODY.PEEK[])')
            if typ!='OK':raise RuntimeError('fetch failed')
            raw=next(x[1] for x in items if isinstance(x,tuple))
            email_message(raw,key+':'+uid.decode())
            cursor(key,uid.decode())

if __name__=='__main__':
    # One worker only. Sources fail independently; no exception logs contain credentials.
    while True:
        for name,fn in [('telegram',telegram_poll),('email',email_poll)]:
            try:fn()
            except Exception as e:print(name,type(e).__name__,flush=True)
        for _ in range(20):
            if not process_one():break
        time.sleep(5)

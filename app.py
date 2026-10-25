import os, secrets, time
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel, Field, field_validator
from core import connect, ingest

app=FastAPI(title='Единая очередь заявок', docs_url=None, redoc_url=None, openapi_url=None)

def auth(authorization:str=Header(default='')):
    token=os.getenv('ADMIN_TOKEN','')
    if len(token)<32 or not secrets.compare_digest(authorization.encode('utf-8'),('Bearer '+token).encode('utf-8')):
        raise HTTPException(401,'Нужен токен доступа')

def ingest_auth(authorization:str=Header(default='')):
    token=os.getenv('INGEST_TOKEN','')
    if len(token)<32 or not secrets.compare_digest(authorization.encode('utf-8'),('Bearer '+token).encode('utf-8')):
        raise HTTPException(401,'Нужен токен приёма заявок')

class Lead(BaseModel):
    external_id:str=Field(min_length=1,max_length=200)
    contact:str=Field(min_length=1,max_length=500)
    text:str=Field(min_length=1,max_length=20000)

    @field_validator('external_id', 'contact', 'text')
    @classmethod
    def reject_blank(cls, value):
        if not value.strip():
            raise ValueError('Blank fields are not allowed')
        return value

@app.post('/api/form',dependencies=[Depends(ingest_auth)])
def form(item:Lead):
    try:return {'id':ingest('form',item.external_id,item.contact,item.text)}
    except ValueError:raise HTTPException(409,'Идентификатор уже использован с другими данными')

@app.get('/api/leads',dependencies=[Depends(auth)])
def leads():
    with connect() as c:return [dict(r) for r in c.execute('SELECT * FROM leads ORDER BY created DESC LIMIT 200')]

@app.get('/api/leads/{ident}/events',dependencies=[Depends(auth)])
def events(ident:str):
    with connect() as c:return [dict(r) for r in c.execute('SELECT * FROM events WHERE lead_id=? ORDER BY at',(ident,))]

@app.post('/api/leads/{ident}/approve',dependencies=[Depends(auth)])
def approve(ident:str):
    with connect() as c:
        result=c.execute("UPDATE leads SET status='approved',updated=? WHERE id=? AND status='review'",(time.time(),ident))
        if not result.rowcount:raise HTTPException(409,'Заявка не готова к согласованию')
        c.execute('INSERT INTO events VALUES(?,?,?)',(ident,time.time(),'approved_no_send'))
    return {'status':'approved','sent':False}

@app.get('/health')
def health():return {'status':'ok'}

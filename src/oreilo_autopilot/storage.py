"""SQLite-backed task registry with WAL, atomic transitions and searchable history."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

def utc(): return datetime.now(timezone.utc).isoformat()

class TaskStore:
    def __init__(self, path='artifacts/autopilot.db'):
        self.path=str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS tasks (
              id TEXT PRIMARY KEY, task TEXT NOT NULL, start_url TEXT NOT NULL,
              domains TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL,
              updated TEXT NOT NULL, result TEXT, error TEXT);
              CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks(status,created);
              CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
              timestamp TEXT NOT NULL, type TEXT NOT NULL, data TEXT NOT NULL);
              CREATE INDEX IF NOT EXISTS ix_events_task ON events(task_id,id);""")
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        return db
    def create(self,task,start_url,domains,task_id=None):
        task_id=task_id or uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)',
                (task_id,task,start_url,json.dumps(domains),'queued',utc(),utc(),None,None))
        return task_id
    def transition(self,task_id,status,result=None,error=None):
        with self.connect() as db:
            cur=db.execute('UPDATE tasks SET status=?,updated=?,result=?,error=? WHERE id=?',
                (status,utc(),json.dumps(result,default=str) if result is not None else None,error,task_id))
            if not cur.rowcount: raise KeyError(task_id)
    def get(self,task_id):
        with self.connect() as db: row=db.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
        if not row: raise KeyError(task_id)
        item=dict(row);item['domains']=json.loads(item['domains']);item['result']=json.loads(item['result']) if item['result'] else None
        return item
    def list(self,limit=50,status=None):
        limit=max(1,min(int(limit),200))
        with self.connect() as db:
            if status: rows=db.execute('SELECT id,task,start_url,status,created,updated,error FROM tasks WHERE status=? ORDER BY created DESC LIMIT ?',(status,limit)).fetchall()
            else: rows=db.execute('SELECT id,task,start_url,status,created,updated,error FROM tasks ORDER BY created DESC LIMIT ?',(limit,)).fetchall()
        return [dict(row) for row in rows]
    def event(self,task_id,kind,data):
        with self.connect() as db: db.execute('INSERT INTO events(task_id,timestamp,type,data) VALUES (?,?,?,?)',(task_id,utc(),kind,json.dumps(data,default=str)))
    def events(self,task_id):
        with self.connect() as db: rows=db.execute('SELECT timestamp,type,data FROM events WHERE task_id=? ORDER BY id',(task_id,)).fetchall()
        return [{**dict(r),'data':json.loads(r['data'])} for r in rows]

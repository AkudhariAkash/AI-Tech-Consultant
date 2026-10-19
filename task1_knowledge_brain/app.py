from __future__ import annotations
import hashlib, json, os, re, sqlite3, time
from datetime import datetime, timezone
from typing import Any
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB=os.getenv("KB_DB",os.path.join(os.path.dirname(__file__),"knowledge.db")); app=FastAPI(title="Knowledge Brain",version="1.0.0")
ALLOWED_ORIGINS=[x.strip() for x in os.getenv("FRONTEND_URL","http://localhost:8081,http://127.0.0.1:8081").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS articles(url TEXT PRIMARY KEY,title TEXT,text TEXT,updated TEXT,content_hash TEXT,active INTEGER DEFAULT 1,images TEXT DEFAULT '[]')")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS article_search USING fts5(url UNINDEXED,title,text)")
    c.execute("CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,question TEXT,answer TEXT,source TEXT,created TEXT)"); c.commit(); return c
class IngestRequest(BaseModel):
    urls:list[str]=Field(default_factory=list); sitemap_url:str|None=None; max_pages:int=Field(50,ge=1,le=500); delay_ms:int=Field(200,ge=0,le=5000)
class Query(BaseModel): question:str=Field(min_length=3); top_k:int=Field(5,ge=1,le=10)
class Feedback(BaseModel): question:str; answer:str; source:str="human"
def parse_page(url,html):
    soup=BeautifulSoup(html,"lxml")
    for node in soup(["script","style","nav","footer"]): node.decompose()
    title=(soup.title.string if soup.title and soup.title.string else url).strip(); text=re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
    images=[{"src":i.get("src"),"alt":i.get("alt","")} for i in soup.find_all("img") if i.get("src")]
    return {"url":url,"title":title,"text":text[:100000],"images":images}
def upsert(item):
    c=conn(); h=hashlib.sha256(item["text"].encode()).hexdigest(); old=c.execute("SELECT content_hash FROM articles WHERE url=?",(item["url"],)).fetchone()
    if old and old["content_hash"]==h: return
    c.execute("INSERT INTO articles(url,title,text,updated,content_hash,active,images) VALUES(?,?,?,?,?,1,?) ON CONFLICT(url) DO UPDATE SET title=excluded.title,text=excluded.text,updated=excluded.updated,content_hash=excluded.content_hash,active=1,images=excluded.images",(item["url"],item["title"],item["text"],datetime.now(timezone.utc).isoformat(),h,json.dumps(item["images"])))
    c.execute("DELETE FROM article_search WHERE url=?",(item["url"],)); c.execute("INSERT INTO article_search VALUES(?,?,?)",(item["url"],item["title"],item["text"])); c.commit()
@app.get("/health")
def health(): return {"ok":True,"active_articles":conn().execute("SELECT count(*) n FROM articles WHERE active=1").fetchone()["n"]}
@app.post("/demo-seed")
def demo_seed():
    items=[("demo://payments/refunds","Refunds and cancellations","Refund requests are reviewed by the support team. Cancel before the next billing date from Settings > Billing. The refund policy depends on the plan and payment provider."),("demo://design/search","Search settings","Search can be configured from Admin > Design > Search. You can change filters, labels, and the default sort order without custom code."),("demo://members/import","Member imports","Admins can import members from CSV in Admin > Members > Import. The CSV must include an email column and duplicate emails are skipped."),("demo://domains/custom","Custom domains","Connect a custom domain from Settings > Domains. Add the displayed DNS records, wait for propagation, then click Verify.")]
    for url,title,text in items: upsert({"url":url,"title":title,"text":text,"images":[]})
    return health()
@app.post("/ingest")
async def ingest(req:IngestRequest):
    urls=list(req.urls)
    if req.sitemap_url:
        async with httpx.AsyncClient(timeout=20,follow_redirects=True) as client: xml=(await client.get(req.sitemap_url)).text
        urls+=re.findall(r"<loc>\s*(.*?)\s*</loc>",xml,flags=re.I)
    urls=list(dict.fromkeys(urls))[:req.max_pages]; done=[]; failed=[]
    async with httpx.AsyncClient(timeout=20,follow_redirects=True,headers={"User-Agent":"AI-Tech-Consultant/1.0"}) as client:
        for url in urls:
            try: r=await client.get(url); r.raise_for_status(); upsert(parse_page(url,r.text)); done.append(url)
            except Exception as e: failed.append({"url":url,"error":str(e)})
            time.sleep(req.delay_ms/1000)
    return {"ingested":done,"failed":failed,"count":len(done)}
@app.post("/query")
def query(q:Query):
    c=conn(); terms=[x for x in re.findall(r"[\w-]{3,}",q.question.lower()) if x not in {"what","how","the","and","for","does"}]
    rows=c.execute("SELECT a.url,a.title,a.text,a.images FROM articles a JOIN article_search s ON a.url=s.url WHERE a.active=1 AND s.text MATCH ? LIMIT ?",(" OR ".join(terms) or "*",q.top_k)).fetchall() if terms else []
    sources=[]
    for r in rows:
        snippets=[]
        for term in terms[:4]:
            m=re.search(r".{0,120}"+re.escape(term)+r".{0,220}",r["text"],re.I)
            if m: snippets.append(m.group(0))
        sources.append({"url":r["url"],"title":r["title"],"snippet":" ".join(snippets)[:700],"images":json.loads(r["images"] or "[]")[:3]})
    if not sources: return {"answer":"I don't know from the connected knowledge base. A human expert should review this question.","grounded":False,"sources":[],"human_task":{"question":q.question,"status":"open"}}
    return {"answer":"Based on the connected help content: "+sources[0]["snippet"],"grounded":True,"sources":sources,"human_task":None}
@app.post("/feedback")
def feedback(f:Feedback):
    c=conn(); c.execute("INSERT INTO feedback(question,answer,source,created) VALUES(?,?,?,?)",(f.question,f.answer,f.source,datetime.now(timezone.utc).isoformat())); c.commit(); return {"stored":True}

from __future__ import annotations
import os, re, uuid
from typing import Any
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
KB=os.getenv("KB_URL","http://localhost:8000"); app=FastAPI(title="Meeting to Scope",version="1.0.0")
ALLOWED_ORIGINS=[x.strip() for x in os.getenv("FRONTEND_URL","http://localhost:8081,http://127.0.0.1:8081").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
class BuildRequest(BaseModel): transcript:str=Field(min_length=20); previous_scope:dict[str,Any]|None=None
class Approval(BaseModel): approved:bool; reviewer:str="human"
def lines(text): return [x.strip(" -*\t") for x in text.splitlines() if x.strip()]
async def kb(q):
    try:
        async with httpx.AsyncClient(timeout=10) as c: return (await c.post(KB+"/query",json={"question":q})).json()
    except Exception as e: return {"answer":"Knowledge service unavailable","grounded":False,"sources":[],"error":str(e)}
def extract(text):
    out=[x for x in lines(text) if re.search(r"need|want|must|should|require|add|change|integrat|search|import|domain|refund",x,re.I)]
    return out[:20] or lines(text)[:10]
@app.get("/health")
def health(): return {"ok":True,"knowledge_api":KB}
@app.post("/build")
async def build(req:BuildRequest):
    reqs=extract(req.transcript); checks=[await kb(r) for r in reqs]; items=[]
    for i,r in enumerate(reqs):
        setting=checks[i].get("grounded",False); items.append({"id":f"REQ-{i+1:02}","requirement":r,"delivery":"configure existing product setting" if setting else "custom implementation / discovery","hours":2 if setting else 8,"knowledge_sources":checks[i].get("sources",[])})
    scope={"id":str(uuid.uuid4())[:8],"status":"pending_approval","assumptions":["Client supplies access and content","One review cycle included"],"in_scope":items,"out_of_scope":["Unspecified integrations","Production support beyond launch"]}
    estimate={"hours":sum(x["hours"] for x in items),"tasks":[{"task":x["requirement"],"hours":x["hours"]} for x in items],"confidence":"medium"}
    proposal={"title":"AI Tech Consultant implementation proposal","summary":f"Deliver {len(items)} prioritized requirements.","price":estimate["hours"]*75,"currency":"USD","next_step":"Human review and client approval"}
    diff=[]
    if req.previous_scope:
        old={x["requirement"] for x in req.previous_scope.get("in_scope",[])}; new={x["requirement"] for x in items}
        diff=[{"change":"new","requirement":x} for x in sorted(new-old)]+[{"change":"removed","requirement":x} for x in sorted(old-new)]
    return {"scope":scope,"estimate":estimate,"proposal":proposal,"changes":diff,"requires_human_approval":True}
@app.post("/approve")
def approve(a:Approval): return {"approved":a.approved,"reviewer":a.reviewer,"client_delivery":"enabled" if a.approved else "blocked"}

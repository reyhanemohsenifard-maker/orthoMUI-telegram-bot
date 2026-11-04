import json, os, urllib.request
from flask import Flask, request, jsonify

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
API = f"https://api.telegram.org/bot{TOKEN}"
with open("content.json", encoding="utf-8") as f:
    DATA = json.load(f)
SITE_URL = DATA.get("site_url", "https://bone-care-compass.lovable.app/")
CATEGORIES = {c["id"]: c for c in DATA.get("categories", [])}
ARTICLES = DATA.get("articles", [])
app = Flask(__name__)

def tg(method, payload):
    req = urllib.request.Request(API + "/" + method,
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def b(text, data=None, url=None):
    obj={"text":text}
    if data: obj["callback_data"]=data
    if url: obj["url"]=url
    return obj

def menu():
    return {"inline_keyboard":[
        [b("🦴 بیماری‌ها و دردها","cat:pain"), b("🏃 تمرین‌های درمانی","cat:exercise")],
        [b("🏥 مراقبت‌های جراحی","cat:surgery"), b("❓ پرسش‌های متداول","cat:faq")],
        [b("🔎 جست‌وجوی مطالب","search"), b("🌐 باز کردن سایت",url=SITE_URL)]
    ]}
def back():
    return {"inline_keyboard":[[b("⬅️ منوی اصلی","home")]]}
def send(chat_id, text, markup=None):
    p={"chat_id":chat_id,"text":text,"disable_web_page_preview":True}
    if markup: p["reply_markup"]=markup
    tg("sendMessage",p)
def search(q):
    terms=[x.casefold() for x in q.split() if len(x)>1]
    found=[]
    for a in ARTICLES:
        hay=(a.get("title","")+" "+a.get("text","")+" "+CATEGORIES.get(a.get("category",""),{}).get("title","")).casefold()
        score=sum(t in hay for t in terms)
        if score: found.append((score,a))
    return [a for _,a in sorted(found,key=lambda x:x[0],reverse=True)[:15]]
def article_keyboard(items):
    rows=[[b("📄 "+a["title"][:55],"article:"+a["id"])] for a in items]
    rows.append([b("⬅️ منوی اصلی","home")])
    return {"inline_keyboard":rows}
def send_article(chat_id,a):
    text="📘 "+a["title"]+"\n\n"+a.get("text","")+"\n\n⚕️ این محتوا آموزشی است و جایگزین معاینه یا دستور پزشک نیست."
    image=a.get("image_url","").strip()
    if image.startswith(("https://","http://")):
        try:
            tg("sendPhoto",{"chat_id":chat_id,"photo":image,"caption":text[:1000],"reply_markup":back()})
            return
        except Exception:
            pass
    send(chat_id,text,back())
def handle_message(m):
    chat=m.get("chat",{}); cid=chat.get("id"); text=(m.get("text") or "").strip()
    if not cid: return
    if text in ("/start","/menu","منو","منوی اصلی"):
        send(cid,DATA.get("welcome","به راهنمای ارتوپدی خوش آمدید."),menu())
    elif text=="/help":
        send(cid,"از منو استفاده کنید یا عبارت موردنظر را برای جست‌وجو بفرستید.",menu())
    else:
        results=search(text.removeprefix("/search ").strip())
        if results: send(cid,"🔎 نتایج مرتبط با «"+text[:100]+"»:",article_keyboard(results))
        else: send(cid,"مطلبی پیدا نشد یا هنوز برای این موضوع محتوایی ثبت نشده است.",menu())
def handle_callback(q):
    cid=q.get("message",{}).get("chat",{}).get("id"); d=q.get("data","")
    try: tg("answerCallbackQuery",{"callback_query_id":q["id"]})
    except Exception: pass
    if not cid: return
    if d=="home": send(cid,DATA.get("welcome","منوی اصلی"),menu())
    elif d=="search": send(cid,"عبارت موردنظر را در همین گفتگو بفرستید؛ مثلاً: درد زانو، کمردرد یا مراقبت پس از جراحی.",back())
    elif d.startswith("cat:"):
        catid=d.split(":",1)[1]; cat=CATEGORIES.get(catid)
        items=[a for a in ARTICLES if a.get("category")==catid]
        if items: send(cid,(cat or {}).get("title","مطالب")+"\nیک مطلب را انتخاب کنید:",article_keyboard(items))
        else: send(cid,(cat or {}).get("title","این بخش")+"\n\nهنوز مطلبی در این بخش ثبت نشده است.",back())
    elif d.startswith("article:"):
        a=next((x for x in ARTICLES if x.get("id")==d.split(":",1)[1]),None)
        if a: send_article(cid,a)
        else: send(cid,"مطلب پیدا نشد.",menu())

@app.get("/")
def health():
    return "OrthoMUI bot is running", 200

@app.post("/telegram-webhook")
def webhook():
    if WEBHOOK_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return jsonify({"ok":False}), 403
    update=request.get_json(silent=True) or {}
    try:
        if "message" in update: handle_message(update["message"])
        elif "callback_query" in update: handle_callback(update["callback_query"])
    except Exception as e:
        app.logger.exception("Update failed: %s",e)
    return jsonify({"ok":True}), 200

from flask import Flask, render_template, request, session, redirect, url_for
import asyncio, threading, json, os
import bot

app = Flask(__name__)
app.secret_key = "gizli_key_2025"
loop = asyncio.new_event_loop()

KULLANICI_DOSYASI = "templates/users.json"

def kullanicilari_yukle():
    if os.path.exists(KULLANICI_DOSYASI):
        with open(KULLANICI_DOSYASI, "r") as f:
            return json.load(f)
    return {}

def kullanicilari_kaydet(veri):
    with open(KULLANICI_DOSYASI, "w") as f:
        json.dump(veri, f, indent=2)

async def baslat_bot():
    await bot.client.connect()
    if not await bot.client.is_user_authorized():
        print("‼️ Giriş başarısız. String session geçersiz olabilir.")
    else:
        print("✅ Bot Telegram'a başarıyla bağlandı.")

def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(baslat_bot())
    loop.run_forever()

threading.Thread(target=run_loop, daemon=True).start()

def free_yetki():
    tip = session.get("tip")
    print(f"DEBUG free_yetki(): session tip = {tip}")
    return tip in ["vip", "free"]

def vip_yetki():
    tip = session.get("tip")
    print(f"DEBUG vip_yetki(): session tip = {tip}")
    return tip == "vip"

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('giris'))
    return render_template('index.html', kullanici=session['username'], tip=session.get('tip', 'free'))

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici = request.form['kullanici']
        sifre = request.form['sifre']
        veriler = kullanicilari_yukle()
        if kullanici in veriler and veriler[kullanici]['sifre'] == sifre:
            session['username'] = kullanici
            session['tip'] = veriler[kullanici].get('tip', 'free')
            print(f"DEBUG: Kullanıcı {kullanici} girdi, tip: {session['tip']}")
            return redirect(url_for('index'))
        else:
            return render_template('giris.html', hata="❌ Bilgiler yanlış")
    return render_template('giris.html')

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        kullanici = request.form['kullanici']
        sifre = request.form['sifre']
        veriler = kullanicilari_yukle()
        if kullanici in veriler:
            return '🚫 Bu kullanıcı zaten var!'
        veriler[kullanici] = {'sifre': sifre, 'tip': 'free'}
        kullanicilari_kaydet(veriler)
        return redirect('/giris')
    return render_template('kayit.html')

@app.route('/abonelik')
def abonelik():
    if 'username' not in session:
        return redirect('/giris')
    return render_template("abonelik.html", kullanici=session['username'], tip=session['tip'])

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris'))

### === FREE ===

@app.route("/adsoyad", methods=["GET", "POST"])
def adsoyad_sayfa():
    if not free_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        ad = request.form["ad"]
        soyad = request.form["soyad"]
        il = request.form["il"]
        ilce = request.form["ilce"]
        komut = f"/adsoyad {ad} {soyad} {il} {ilce}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("adsoyad.html", sonuc=sonuc)

@app.route("/tc", methods=["GET", "POST"])
def tc_sayfa():
    if not free_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        tc = request.form["tc"]
        komut = f"/tc {tc}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("tc.html", sonuc=sonuc)

@app.route("/adres", methods=["GET", "POST"])
def adres_sayfa():
    if not free_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        adres = request.form["adres"]
        komut = f"/adres {adres}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("adres.html", sonuc=sonuc)

@app.route("/aile", methods=["GET", "POST"])
def aile_sayfa():
    if not free_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        soyad = request.form["soyad"]
        komut = f"/aile {soyad}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("aile.html", sonuc=sonuc)

@app.route("/gsmtc", methods=["GET", "POST"])
def gsm_sayfa():
    if not free_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        gsm = request.form["gsm"]
        komut = f"/gsm {gsm}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("gsm.html", sonuc=sonuc)

### === VIP ===

@app.route("/iban", methods=["GET", "POST"])
def iban():
    print("DEBUG iban sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        iban = request.form["iban"]
        komut = f"/iban {iban}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("iban.html", sonuc=sonuc)

@app.route("/ip", methods=["GET", "POST"])
def ip():
    print("DEBUG ip sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        ip = request.form["ip"]
        komut = f"/ip {ip}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("ip.html", sonuc=sonuc)

@app.route("/burc", methods=["GET", "POST"])
def burc():
    print("DEBUG burc sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        burc = request.form["burc"]
        komut = f"/burc {burc}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("burc.html", sonuc=sonuc)

@app.route("/jandarma", methods=["GET", "POST"])
def jandarma():
    print("DEBUG jandarma sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        konum = request.form["konum"]
        detay = request.form["detay"]
        future = asyncio.run_coroutine_threadsafe(bot.gonder_jandarma_ihbar(konum, detay), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("jandarma.html", sonuc=sonuc)

@app.route("/egm", methods=["GET", "POST"])
def egm():
    print("DEBUG egm sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        konum = request.form["konum"]
        detay = request.form["detay"]
        future = asyncio.run_coroutine_threadsafe(bot.gonder_egm_ihbar(konum, detay), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("egm.html", sonuc=sonuc)

@app.route("/usom", methods=["GET", "POST"])
def usom():
    print("DEBUG usom sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        konum = request.form["konum"]
        detay = request.form["detay"]
        future = asyncio.run_coroutine_threadsafe(bot.gonder_usom_ihbar(konum, detay), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("usom.html", sonuc=sonuc)

@app.route("/tcgsm", methods=["GET", "POST"])
def tcgsm():
    print("DEBUG tcgsm sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        tc = request.form["tc"]
        komut = f"/tcgsm {tc}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("tcgsm.html", sonuc=sonuc)

@app.route("/cocuk", methods=["GET", "POST"])
def cocuk():
    print("DEBUG cocuk sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        ad = request.form["ad"]
        soyad = request.form["soyad"]
        komut = f"/cocuk {ad} {soyad}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("cocuk.html", sonuc=sonuc)

@app.route("/smsbomber", methods=["GET", "POST"])
def smsbomber():
    print("DEBUG smsbomber sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        gsm = request.form["gsm"]
        komut = f"/smsbomber {gsm}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("smsbomber.html", sonuc=sonuc)

@app.route("/call", methods=["GET", "POST"])
def call():
    print("DEBUG call sayfası çağrıldı, vip_yetki:", vip_yetki())
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    if request.method == "POST":
        gsm = request.form["gsm"]
        komut = f"/call {gsm}"
        future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
        try:
            sonuc = future.result(timeout=60)
        except Exception as e:
            sonuc = f"Hata oluştu: {e}"
    return render_template("call.html", sonuc=sonuc)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

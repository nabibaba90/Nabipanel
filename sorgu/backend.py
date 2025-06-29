from flask import Flask, render_template, request, session, redirect, url_for, jsonify import asyncio, threading, json, os from datetime import datetime import bot

app = Flask(name) app.secret_key = "gizli_key_2025" loop = asyncio.new_event_loop()

KULLANICI_DOSYASI = "sorgu/users.json" SIPARIS_DOSYASI = "siparisler.json"

def kullanicilari_yukle(): if os.path.exists(KULLANICI_DOSYASI): with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as f: return json.load(f) return {}

def kullanicilari_kaydet(veri): with open(KULLANICI_DOSYASI, "w", encoding="utf-8") as f: json.dump(veri, f, indent=2, ensure_ascii=False)

def siparisleri_yukle(): if os.path.exists(SIPARIS_DOSYASI): with open(SIPARIS_DOSYASI, "r", encoding="utf-8") as f: return json.load(f) return []

def siparisleri_kaydet(veri): with open(SIPARIS_DOSYASI, "w", encoding="utf-8") as f: json.dump(veri, f, indent=2, ensure_ascii=False)

def free_yetki(): tip = session.get("tip") return tip in ["vip", "free", "kurucu"]

def vip_yetki(): tip = session.get("tip") return tip in ["vip", "kurucu"]

def kurucu_yetki(): tip = session.get("tip") return tip == "kurucu"

@app.route('/') def index(): if 'username' not in session: return redirect(url_for('giris')) return render_template('index.html', kullanici=session['username'], tip=session.get('tip', 'free'))

@app.route('/giris', methods=['GET', 'POST']) def giris(): if request.method == 'POST': kullanici = request.form['kullanici'] sifre = request.form['sifre'] veriler = kullanicilari_yukle() if kullanici in veriler and veriler[kullanici]['sifre'] == sifre: session['username'] = kullanici session['tip'] = veriler[kullanici].get('tip', 'free') return redirect(url_for('index')) else: return render_template('giris.html', hata="❌ Bilgiler yanlış") return render_template('giris.html')

@app.route('/cikis') def cikis(): session.clear() return redirect(url_for('giris'))

@app.route('/takipci', methods=['GET', 'POST']) def instagram_takipci(): if not vip_yetki(): return redirect('/abonelik') mesaj = "" if request.method == "POST": hedef = request.form.get("hedef") islem = "Takipçi" siparisler = siparisleri_yukle() siparisler.append({ "kullanici": session["username"], "hedef": hedef, "islem": islem, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M") }) siparisleri_kaydet(siparisler) mesaj = f"✅ {hedef} için {islem} siparişi alındı." return render_template("takipci.html", mesaj=mesaj)

@app.route('/begeni', methods=['GET', 'POST']) def instagram_begeni(): if not vip_yetki(): return redirect('/abonelik') mesaj = "" if request.method == "POST": hedef = request.form.get("hedef") islem = "Beğeni" siparisler = siparisleri_yukle() siparisler.append({ "kullanici": session["username"], "hedef": hedef, "islem": islem, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M") }) siparisleri_kaydet(siparisler) mesaj = f"✅ {hedef} için {islem} siparişi alındı." return render_template("begeni.html", mesaj=mesaj)

@app.route('/izlenme', methods=['GET', 'POST']) def instagram_izlenme(): if not vip_yetki(): return redirect('/abonelik') mesaj = "" if request.method == "POST": hedef = request.form.get("hedef") islem = "İzlenme" siparisler = siparisleri_yukle() siparisler.append({ "kullanici": session["username"], "hedef": hedef, "islem": islem, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M") }) siparisleri_kaydet(siparisler) mesaj = f"✅ {hedef} için {islem} siparişi alındı." return render_template("izlenme.html", mesaj=mesaj)

@app.route('/siparisler') def siparisler(): if not kurucu_yetki(): return "🚫 Bu sayfaya erişim yetkiniz yok." siparisler = siparisleri_yukle() return render_template('siparisler.html', siparisler=siparisler)

if name == 'main': app.run(host="0.0.0.0", port=5000, debug=True)


# --- Admin Panel ---
@app.route('/admin')
def admin_panel():
    if not vip_yetki():
        return redirect(url_for('abonelik'))
    kullanicilar = kullanicilari_yukle()
    aktif_kullanici_sayisi = len(kullanicilar)
    vip_kullanicilar = [k for k, v in kullanicilar.items() if v.get('tip') == 'vip']
    free_kullanicilar = [k for k, v in kullanicilar.items() if v.get('tip') == 'free']
    kurucu_kullanicilar = [k for k, v in kullanicilar.items() if v.get('tip') == 'kurucu']
    return render_template('admin.html',
                           kullanicilar=kullanicilar,
                           aktif_sayi=aktif_kullanici_sayisi,
                           vip_list=vip_kullanicilar,
                           free_list=free_kullanicilar,
                           kurucu_list=kurucu_kullanicilar,
                           kullanici=session['username'],
                           tip=session.get('tip'))

@app.route('/admin/kullanici_ekle', methods=['POST'])
def admin_kullanici_ekle():
    if not kurucu_yetki():
        return jsonify({"error": "Yetkisiz"}), 403
    data = request.form
    kullanici = data.get('kullanici')
    sifre = data.get('sifre')
    tip = data.get('tip')
    if not kullanici or not sifre or not tip:
        return jsonify({"error": "Eksik veri"}), 400
    kullanicilar = kullanicilari_yukle()
    if kullanici in kullanicilar:
        return jsonify({"error": "Kullanıcı zaten var"}), 400
    kullanicilar[kullanici] = {"sifre": sifre, "tip": tip}
    kullanicilari_kaydet(kullanicilar)
    return jsonify({"message": "Kullanıcı eklendi."})

@app.route('/admin/kullanici_sil/<kullanici>', methods=['POST'])
def admin_kullanici_sil(kullanici):
    if not kurucu_yetki():
        return jsonify({"error": "Yetkisiz"}), 403
    kullanicilar = kullanicilari_yukle()
    if kullanici not in kullanicilar:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    if kullanicilar[kullanici].get('tip') == 'kurucu':
        return jsonify({"error": "Kurucu silinemez"}), 400
    del kullanicilar[kullanici]
    kullanicilari_kaydet(kullanicilar)
    return jsonify({"message": "Kullanıcı silindi."})

@app.route('/admin/kullanici_tip_degistir', methods=['POST'])
def admin_kullanici_tip_degistir():
    if not kurucu_yetki():
        return jsonify({"error": "Yetkisiz"}), 403
    data = request.form
    kullanici = data.get('kullanici')
    tip = data.get('tip')
    if not kullanici or not tip:
        return jsonify({"error": "Eksik veri"}), 400
    kullanicilar = kullanicilari_yukle()
    if kullanici not in kullanicilar:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    kullanicilar[kullanici]['tip'] = tip
    kullanicilari_kaydet(kullanicilar)
    return jsonify({"message": "Kullanıcı tipi güncellendi."})

# Diğer mevcut route'larınızı da aynen koruyabilirsiniz...

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

BEGENI_KAYIT_DOSYASI = "begeni_kayit.json"

def begeni_kayit_yukle():
    if os.path.exists(BEGENI_KAYIT_DOSYASI):
        with open(BEGENI_KAYIT_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def begeni_kayit_kaydet(veri):
    with open(BEGENI_KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)

@app.route("/begeni", methods=["GET", "POST"])
def instagram_begeni():
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    kullanici = session.get("username")
    bugun = datetime.now().strftime("%Y-%m-%d")

    if request.method == "POST":
        hedef = request.form["hedef"]
        kayitlar = begeni_kayit_yukle()

        if kayitlar.get(kullanici) == bugun:
            sonuc = "🚫 Zaten bugün 100 beğeni gönderimi yaptınız. Yarın tekrar deneyin."
        else:
            komut = f"/begeni {hedef}"
            future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
            try:
                cevap = future.result(timeout=60)
                sonuc = cevap
                kayitlar[kullanici] = bugun
                begeni_kayit_kaydet(kayitlar)
            except Exception as e:
                sonuc = f"Hata oluştu: {e}"

    return render_template("begeni.html", sonuc=sonuc, kullanici=kullanici, tip=session.get("tip"))
TAKIPCI_KAYIT_DOSYASI = "takipci_kayit.json"

def takipci_kayit_yukle():
    if os.path.exists(TAKIPCI_KAYIT_DOSYASI):
        with open(TAKIPCI_KAYIT_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def takipci_kayit_kaydet(veri):
    with open(TAKIPCI_KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)

@app.route("/takipci", methods=["GET", "POST"])
def instagram_takipci():
    if not vip_yetki():
        return redirect("/abonelik")  # Ücretsiz sayfa veya abonelik yönlendirmesi
    sonuc = None
    kullanici = session.get("username")
    bugun = datetime.now().strftime("%Y-%m-%d")

    if request.method == "POST":
        hedef = request.form["hedef"]
        kayitlar = takipci_kayit_yukle()

        if kayitlar.get(kullanici) == bugun:
            sonuc = "🚫 Son 2 günde 1 kez 50 takipçi gönderme hakkınızı kullandınız."
        else:
            komut = f"/takipci {hedef}"
            future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
            try:
                cevap = future.result(timeout=60)
                sonuc = cevap
                kayitlar[kullanici] = bugun
                takipci_kayit_kaydet(kayitlar)
            except Exception as e:
                sonuc = f"Hata oluştu: {e}"

    return render_template("takipci.html", sonuc=sonuc, kullanici=kullanici, tip=session.get("tip"))
IZLENME_KAYIT_DOSYASI = "izlenme_kayit.json"

def izlenme_kayit_yukle():
    if os.path.exists(IZLENME_KAYIT_DOSYASI):
        with open(IZLENME_KAYIT_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def izlenme_kayit_kaydet(veri):
    with open(IZLENME_KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)

@app.route("/izlenme", methods=["GET", "POST"])
def instagram_izlenme():
    if not vip_yetki():
        return redirect("/abonelik")
    sonuc = None
    kullanici = session.get("username")
    bugun = datetime.now().strftime("%Y-%m-%d")

    if request.method == "POST":
        hedef = request.form["hedef"]
        kayitlar = izlenme_kayit_yukle()

        if kayitlar.get(kullanici) == bugun:
            sonuc = "🚫 Bugün 1000 izlenme gönderme hakkınızı kullandınız. Yarın tekrar deneyin."
        else:
            komut = f"/izlenme {hedef}"
            future = asyncio.run_coroutine_threadsafe(bot.gonder_ve_bekle(komut), loop)
            try:
                cevap = future.result(timeout=60)
                sonuc = cevap
                kayitlar[kullanici] = bugun
                izlenme_kayit_kaydet(kayitlar)
            except Exception as e:
                sonuc = f"Hata oluştu: {e}"

    return render_template("izlenme.html", sonuc=sonuc, kullanici=kullanici, tip=session.get("tip"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

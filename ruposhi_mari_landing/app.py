from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_key"

STEADFAST_API_KEY = os.getenv("STEADFAST_API_KEY")
STEADFAST_SECRET_KEY = os.getenv("STEADFAST_SECRET_KEY")
STEADFAST_API_URL = os.getenv("STEADFAST_API_URL", "https://portal.packzy.com/api/v1")


def init_db():
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            price INTEGER,
            name TEXT,
            phone TEXT,
            address TEXT,
            quantity INTEGER,
            pack TEXT,
            status TEXT DEFAULT 'Pending',
            courier_sent INTEGER DEFAULT 0,
            consignment_id TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("dthb04.18")


PRODUCTS = [
    {
        "id": 1,
        "name": "The Ordinary Niacinamide 10% + Zinc 1%",
        "price": 990,
        "old_price": 1290,
        "image": "ordinary.jpg",
        "offers": {1: 990, 2: 1890, 3: 2690},
        "details": [
           "✨ দাগহীন উজ্জ্বল ত্বকের সহজ সমাধান – The Ordinary Niacinamide 10% + Zinc 1%",

"এই সিরাম ত্বকের অতিরিক্ত তেল নিয়ন্ত্রণ করে, ব্রণ কমায়, দাগ-পিগমেন্টেশন হালকা করে এবং স্কিনকে আরও bright ও even করে তোলে। Lightweight formula হওয়ায় প্রতিদিনের স্কিনকেয়ারে বা makeup-এর নিচে ব্যবহার করা যায়।",

" Acne & dark spot reduction",
" Oil control & pore tightening",
" Skin barrier strong করে",
" ১-২ সপ্তাহে দৃশ্যমান ফল"

        ],
        "how_to_use": [
            " ১ দিনে ২ বার ব্যবহার করুন ➡ সকাল ও রাত—দু’সময়ই ব্যবহার করা যায়।",

      "মুখ ধোয়ার পরে ব্যবহার করবেন ➡ ফেসওয়াশ বা সাবান দিয়ে মুখ পরিষ্কার করে ভালোভাবে শুকিয়ে নিন।",

"কয়েক ফোঁটা নিন➡ ২–৩ ফোঁটা সিরাম পুরো মুখে ছড়িয়ে হালকা ম্যাসাজ করুন।",

"পুরোপুরি শোষণ না হওয়া পর্যন্ত অপেক্ষা করুন (৩০–৫০ সেকেন্ড)" 
        ],
        "faq":[
            
        ]
    },
    {
        "id": 2,
        "name": "Fiorae Papaya & Gluta Plus Kojic Whitening Soap 165gm",
        "price": 590,
        "old_price": 790,
        "image": "papaya.jpg",
        "offers": {1: 590, 2: 990, 3: 1390},
        "details": [
            "দাগহীন উজ্জ্বল ত্বকের জন্য পারফেক্ট সল্যুশন!ডার্ক স্পট, ব্রণ ও ব্ল্যাকহেড কমায়, অসমান স্কিন টোন ঠিক করে এবং রোদে পোড়া ভাব দূর করে ত্বককে করে ফর্সা ও গ্লোইং। রাফ/ডেড স্কিন রিমুভ করে ত্বককে করে মসৃণ, নরম ও হেলদি।"

        ],
        "how_to_use": [
            "দিনে ২ বার ব্যবহার করুন—সকাল ও রাতে।",

            "সাবানটি ফেস এ লাগিয়ে ২০–৩০ সেকেন্ড হালকা ম্যাসাজ করুন।",

            "এরপর পরিষ্কার পানি দিয়ে ধুয়ে নিন।",

            "খুব শুকনো ত্বকে ব্যবহার করলে ধোয়ার পর ময়েশ্চারাইজার লাগান।",

            "নতুন ব্যবহারকারীরা প্রথম ২–৩ দিন দিনে ১ বার ব্যবহার করুন, এরপর ধীরে ধীরে ২ বার করুন।"
        ],
        "faq":[
            
        ]
    },
 {
        "id": 3,
        "name": "Laikou Japan Sakura Sunscreen, SPF50++ (50 gm)",
        "price": 600,
        "old_price": 700,
        "image": "sunscreen.jpg",
        "offers": {1: 600, 2: 1100, 3: 1500},
        "details": [
            "কালো দাগ ব্রন মেছতা দূর করবে।",
            "আপনার স্কিন কে ফর্সা করবে।",
            "একটা আলাদা মেকাপ লুক দিবে।",
            "এক সপ্তাহ ব্যবহারেই পাবেন ব্রাইট লুক।" 

        ],
        "how_to_use": [
            "বাহিরে যাওয়ার ১০ মিনিট আগে সানস্ক্রিনটি মুখে লাগান।",  
            "রান্না করার আগে ৩০ মিনিট আগে সানস্ক্রিন ব্যবহার করুন।",  
            "দিনের বেলা সানস্ক্রিন ব্যবহার করা অত্যন্ত জরুরি।",  
            "চুলার কাছেও যাওয়ার ৩০ মিনিট আগে সানস্ক্রিন লাগান।",  
            "ত্বককে সুরক্ষিত ও উজ্জ্বল রাখতে নিয়মিত ব্যবহার করুন।"

        ],
        "faq":[
            
        ]
    },
 {
        "id": 4,
        "name": "MIKEO Fiber XS Dietary Supplement Probiotic (30 Sachets)",
        "price": 890,
        "old_price": 1290,
        "image": "juice.jpg",
        "offers": {1: 890, 2: 1590, 3: 2290},
        "details": [
            "পেট ও কোমরের বাড়তি চর্বি দ্রুত কমায় জমে থাকা ফ্যাট ভেঙে শরীরকে করে পারফেক্ট শেপড স্কিনকে করে উজ্জ্বল ও ফর্সা ডায়েট বা ব্যায়াম ছাড়াই কার্যকর (তবে করলে আরও দ্রুত ফল) ১ মাসে ৬–৮ কেজি পর্যন্ত ওজন কমাতে সাহায্য করে ১০০% হারবাল ফর্মুলা – কোনো Side Effects নেই",
            "১ প্যাকেট (৩০ পিস)খেলে ৬-৮ কেজি কমবে", 
            "২ প্যাকেট (৬০ পিস) খেলে ১২-১৫ কেজি কমবে।", 
            "৩ প্যাকেট (৯০ পিস) খেলে ২০-২৫ কেজি ওজন কমবে।" 
            
        ],
        "how_to_use": [
            "১ প্যাকেটে ৩০ পিস থাকবে ১ গ্লাস হালকা গরম পানির সাথে মিশিয়ে প্রতিদিন খাবারের পরে ১ পিস করে খাবেন রাতে ঘুমাতে যাওয়ার আগে।"
        ],
       "faq": [
            {"q": "এক প্যাকেট খেলে কত কেজি ওজন কমে?", "a": "এক প্যাকেটে ৩০ পিস থাকে। নিয়ম মেনে ৩০ দিনে ৩০ পিস খেলে ইনশাআল্লাহ ৬ থেকে ৮ কেজি ওজন কমে।"},
            {"q": "কিভাবে খাবো?", "a": "প্রতিদিন যেকোন সময়ে এক পিস এক গ্লাস পানিতে গুলে খাবেন। খাওয়ার আগে বা পরে যেকন সময় খাওয়া যাবে"},
            {"q": "আসল নকল চিনবো কিভাবে?", "a": "আসল আর নকল টার পার্থক্যের ছবি উপরে দেয়া আছে। আসল টা গাঢ় সবুজ রঙের হবে, আর নকল টা হালকা সবুজ। আসল টার স্বাদ ভালো, কিন্তু নকল টা থেকে গন্ধ আসে।"},
            {"q": "এটার কোন গ্যারান্টি কি দেবেন?", "a": "হ্যা। যদি নকল প্রমাণ করতে পারেন তাহলে সম্পূর্ণ টাকা ফেরত দিবো। মার্কেটে অনেক নকল আছে, কিন্তু আমরা আসলটাই দিবো।"},
            {"q": "গর্ভবতী মহিলারা কি খেতে পারবে?", "a": "না, গর্ভবতী মহিলারা খেতে পারবে না। তবে যারা মা হয়ে শিশুকে দুধ খাওয়াচ্ছেন তারা খেতে পারবেন।"}
            
        ] 

    }
 
    
]


@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return "Product Not Found", 404

    success = False

    if request.method == "POST":
        qty = int(request.form.get("quantity"))
        offer_price = product["offers"].get(qty, product["price"])

        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")

        # Convert Bangla numbers to English
        bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
        phone = phone.translate(bangla_to_english)

        # Validate phone: must be exactly 11 digits
        if not phone.isdigit() or len(phone) != 11:
            return "<script>alert('❌ Phone number must be 11 digits!'); window.history.back();</script>"

        conn = sqlite3.connect("orders.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO orders (product_name, price, name, phone, address, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product["name"], offer_price, name, phone, address, qty
        ))
        conn.commit()
        conn.close()
        success = True

    return render_template("product.html", product=product, success=success)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        if (
            request.form.get("username") == ADMIN_USERNAME and
            check_password_hash(ADMIN_PASSWORD_HASH, request.form.get("password"))
        ):
            session["admin"] = True
            return redirect(url_for("admin_orders"))
        error = "❌ Wrong username or password"
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/orders")
def admin_orders():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()

    return render_template("admin_orders.html", orders=orders)


@app.route("/admin/update/<int:order_id>/<string:status>")
def update_order(order_id, status):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_orders"))


@app.route("/admin/sendcourier/<int:order_id>")
def send_to_courier(order_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = c.fetchone()

    if order[8] != "Confirmed":
        conn.close()
        return "<script>alert('❌ Confirm order first!'); window.location='/admin/orders'</script>"

    invoice = f"ORD{order_id}"
    payload = {
        "invoice": invoice,
        "recipient_name": order[3],
        "recipient_phone": order[4],
        "recipient_address": order[5],
        "cod_amount": order[2],
        "note": f"{order[1]} x{order[6]}",
    }

    headers = {
        "Api-Key": STEADFAST_API_KEY,
        "Secret-Key": STEADFAST_SECRET_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(f"{STEADFAST_API_URL}/create_order", json=payload, headers=headers)
        data = response.json()
        print("Courier API Response:", data)

        if response.status_code == 200 and "consignment" in data:
            consignment_id = data["consignment"]["consignment_id"]
            c.execute("UPDATE orders SET courier_sent=1, consignment_id=? WHERE id=?",
                      (consignment_id, order_id))
            conn.commit()
            conn.close()
            return f"<script>alert('🚚 Sent! Consignment: {consignment_id}'); window.location='/admin/orders'</script>"

        else:
            conn.close()
            return f"<script>alert('❌ Courier Failed: {data}'); window.location='/admin/orders'</script>"

    except Exception as e:
        conn.close()
        return f"<script>alert('❌ Error: {e}'); window.location='/admin/orders'</script>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


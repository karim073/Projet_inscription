from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import os
import csv
import io
import requests
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret-dev-key")

# -----------------------------
# CONFIG
# -----------------------------
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")

admin_user = "admin"
admin_password_plain = os.environ.get("ADMIN_PASSWORD", "admin123")
admin_password = generate_password_hash(admin_password_plain)

DB_NAME = "inscriptions.db"

# -----------------------------
# DATABASE
# -----------------------------
def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        nom_tuteur TEXT,
        prenom_tuteur TEXT,
        email_tuteur TEXT,
        telephone TEXT,
        adresse TEXT,
        ville TEXT,
        allergies TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# MIGRATION DB
# -----------------------------
@app.route("/migrate-db")
def migrate_db():
    conn = get_db()
    try:
        try:
            conn.execute("ALTER TABLE inscriptions ADD COLUMN telephone TEXT DEFAULT ''")
        except:
            pass  # colonne existe déjà
        try:
            conn.execute("ALTER TABLE inscriptions ADD COLUMN adresse TEXT DEFAULT ''")
        except:
            pass  # colonne existe déjà
        try:
            conn.execute("ALTER TABLE inscriptions ADD COLUMN ville TEXT DEFAULT ''")
        except:
            pass  # colonne existe déjà
        conn.commit()
        return "Migration réussie ✅ — colonnes telephone, adresse et ville ajoutées"
    except Exception as e:
        return f"Erreur : {e}"
    finally:
        conn.close()

# -----------------------------
# RESET DB
# -----------------------------
@app.route("/reset-db")
def reset_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    return "Base de données recréée avec succès ✅"

# -----------------------------
# AUTH ADMIN
# -----------------------------
def admin_required():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return None

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == admin_user and check_password_hash(admin_password, password):
            session["admin"] = True
            return redirect(url_for("dashboard"))

    return render_template("login.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM inscriptions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT allergies, COUNT(*) FROM inscriptions GROUP BY allergies")
    stats = cursor.fetchall()

    cursor.execute("SELECT * FROM inscriptions")
    data = cursor.fetchall()

    conn.close()
    return render_template("dashboard.html", total=total, stats=stats, data=data)

# -----------------------------
# EMAIL TUTEUR
# -----------------------------
def envoyer_email_tuteur(email_tuteur, prenom_enfant, nom_tuteur):
    api_key = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN")
    email_from = os.environ.get("EMAIL_FROM")

    if not all([api_key, domain, email_from]):
        print("❌ Variables Mailgun manquantes")
        return

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": email_from,
                "to": email_tuteur,
                "subject": "Confirmation d'inscription",
                "text": f"Bonjour {nom_tuteur},\n\nL'inscription de {prenom_enfant} est confirmée.\n\nMerci."
            },
            timeout=10
        )
        print("Status:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print(f"Erreur email : {e}")

# -----------------------------
# EMAIL ADMIN CSV
# -----------------------------
def envoyer_csv_admin():
    api_key = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN")
    email_from = os.environ.get("EMAIL_FROM")
    email_admin = os.environ.get("EMAIL_ADMIN")

    if not all([api_key, domain, email_from, email_admin]):
        print("❌ Variables Mailgun/admin manquantes")
        return

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nom, prenom, nom_tuteur, prenom_tuteur, email_tuteur, telephone, adresse, ville, allergies FROM inscriptions")
        rows = cursor.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["nom", "prenom", "nom_tuteur", "prenom_tuteur", "email_tuteur", "telephone", "adresse", "ville", "allergies"])
        writer.writerows(rows)
        csv_content = output.getvalue().encode("utf-8")

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            files=[("attachment", ("inscriptions.csv", csv_content, "text/csv"))],
            data={
                "from": email_from,
                "to": email_admin,
                "subject": "Liste des inscriptions",
                "text": "Fichier CSV en pièce jointe."
            },
            timeout=10
        )
        print(f"CSV envoyé : {response.status_code}")
    except Exception as e:
        print(f"Erreur CSV : {e}")

# -----------------------------
# FORMULAIRE
# -----------------------------
@app.route('/')
def formulaire():
    return render_template("inscription.html")

# -----------------------------
# INSCRIPTION
# -----------------------------
@app.route('/inscription', methods=['POST'])
def inscription():
    print("✅ Route /inscription appelée")
    # reCAPTCHA
    token = request.form.get('g-recaptcha-response')
    r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={'secret': RECAPTCHA_SECRET_KEY, 'response': token}
    )
    result = r.json()
    print("reCAPTCHA:", result)

    nom_tuteur = request.form['nom_tuteur']
    prenom_tuteur = request.form['prenom_tuteur']
    email_tuteur = request.form['email_tuteur']
    telephone = request.form.get('tel_tuteur', '')
    adresse = request.form.get('adresse_tuteur', '')
    ville = request.form.get('ville_tuteur', '')
    nb_enfants = int(request.form.get("nb_enfants", 0))

    conn = get_db()
    cursor = conn.cursor()

    for i in range(1, nb_enfants + 1):
        nom_enfant = request.form.get(f"nom_enfant_{i}", "")
        prenom_enfant = request.form.get(f"prenom_enfant_{i}", "")
        allergies = request.form.get(f"allergies_enfant_{i}", "")

        try:
            cursor.execute(
                "INSERT INTO inscriptions (nom, prenom, nom_tuteur, prenom_tuteur, email_tuteur, telephone, adresse, ville, allergies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (nom_enfant, prenom_enfant, nom_tuteur, prenom_tuteur, email_tuteur, telephone, adresse, ville, allergies)
            )
        except Exception as e:
            print("❌ Erreur insertion:", e)
            conn.close()
            return f"Erreur interne : {e}", 500

        envoyer_email_tuteur(email_tuteur, prenom_enfant, nom_tuteur)

    conn.commit()
    conn.close()

    envoyer_csv_admin()

    return render_template("confirmation.html", nom_tuteur=nom_tuteur)

# -----------------------------
# ADMIN SIMPLE
# -----------------------------
@app.route("/admin")
def admin():
    redirect_response = admin_required()
    if redirect_response:
        return redirect_response

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inscriptions")
    data = cursor.fetchall()
    conn.close()
    return render_template("admin.html", data=data)

# -----------------------------
# EXPORT EXCEL
# -----------------------------
@app.route("/export")
def export():
    redirect_response = admin_required()
    if redirect_response:
        return redirect_response

    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM inscriptions", conn)
    conn.close()

    fichier = "participants.xlsx"
    df.to_excel(fichier, index=False)

    return send_file(fichier, as_attachment=True)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
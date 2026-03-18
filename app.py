from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import os
import csv
import requests
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "SECRET123")

# Admin sécurisé
admin_user = "admin"
admin_password = generate_password_hash(os.environ.get("ADMIN_PASSWORD", "1234"))

# -----------------------------
# Initialisation base de données
# -----------------------------
def init_db():
    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()

    # ⚠️ Retirez les 2 lignes suivantes après le premier déploiement réussi
    cursor.execute("DROP TABLE IF EXISTS inscriptions")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS inscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    nom_tuteur TEXT,
    prenom_tuteur TEXT,
    email_tuteur TEXT,
    cours TEXT
)
""")
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Vérification admin
# -----------------------------
def admin_required():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return None

# -----------------------------
# Login admin
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
# Dashboard admin
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inscriptions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT cours, COUNT(*) FROM inscriptions GROUP BY cours")
    stats = cursor.fetchall()
    cursor.execute("SELECT * FROM inscriptions")
    data = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", total=total, stats=stats, data=data)

# -----------------------------
# Fonction envoi email via Mailgun
# -----------------------------
def envoyer_email(email, nom_enfant, nom_tuteur):
    api_key = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN")
    email_from = os.environ.get("EMAIL_FROM")

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": email_from,
                "to": email,
                "subject": "Confirmation d'inscription",
                "text": (
                    f"Bonjour {nom_tuteur},\n\n"
                    f"L'inscription de {nom_enfant} est confirmée.\n\n"
                    "Merci."
                )
            },
            timeout=10
        )
        print(f"Email envoyé : {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erreur envoi email : {e}")

# -----------------------------
# Page formulaire
# -----------------------------
@app.route('/')
def formulaire():
    return render_template("inscription.html")

# -----------------------------
# Traitement inscription
# -----------------------------
@app.route('/inscription', methods=['POST'])
def inscription():
    nom_tuteur = request.form['nom_tuteur']
    prenom_tuteur = request.form['prenom_tuteur']
    email_tuteur = request.form['email_tuteur']
    tel_tuteur = request.form['tel_tuteur']
    nb_enfants = int(request.form.get("nb_enfants", 0))

    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()

    for i in range(1, nb_enfants + 1):
        nom_enfant = request.form.get(f"nom_enfant_{i}", "")
        prenom_enfant = request.form.get(f"prenom_enfant_{i}", "")
        allergies = request.form.get(f"allergies_enfant_{i}", "")

        cursor.execute(
            "INSERT INTO inscriptions (nom, prenom, nom_tuteur, prenom_tuteur, email_tuteur, cours) VALUES (?, ?, ?, ?, ?, ?)",
            (nom_enfant, prenom_enfant, nom_tuteur, prenom_tuteur, email_tuteur, allergies)
        )

        fichier_existe = os.path.exists("data.csv") and os.path.getsize("data.csv") > 0
        with open("data.csv", "a", newline='', encoding='utf-8') as f:
            fieldnames = ["nom_tuteur", "prenom_tuteur", "email_tuteur", "tel_tuteur",
                          "nom_enfant", "prenom_enfant", "allergies"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not fichier_existe:
                writer.writeheader()
            writer.writerow({
                "nom_tuteur": nom_tuteur,
                "prenom_tuteur": prenom_tuteur,
                "email_tuteur": email_tuteur,
                "tel_tuteur": tel_tuteur,
                "nom_enfant": nom_enfant,
                "prenom_enfant": prenom_enfant,
                "allergies": allergies
            })

        envoyer_email(email_tuteur, nom_enfant, nom_tuteur)

    conn.commit()
    conn.close()

    return render_template("confirmation.html", nom_tuteur=nom_tuteur)

# -----------------------------
# Page admin simple
# -----------------------------
@app.route("/admin")
def admin():
    redirect_response = admin_required()
    if redirect_response:
        return redirect_response

    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inscriptions")
    data = cursor.fetchall()
    conn.close()

    return render_template("admin.html", data=data)

# -----------------------------
# Export Excel
# -----------------------------
@app.route("/export")
def export():
    redirect_response = admin_required()
    if redirect_response:
        return redirect_response

    conn = sqlite3.connect("inscriptions.db")
    df = pd.read_sql_query("SELECT * FROM inscriptions", conn)
    fichier = "participants.xlsx"
    df.to_excel(fichier, index=False)
    conn.close()

    return send_file(fichier, as_attachment=True)

# -----------------------------
# Lancement serveur
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

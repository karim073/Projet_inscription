from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
import csv
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()  # ← charge automatiquement le fichier .env

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")  # nécessaire pour session

# Admin sécurisé
admin_user = "admin"
admin_password = generate_password_hash(os.environ.get("ADMIN_PASSWORD"))

# -----------------------------
# Initialisation base de données
# -----------------------------
def init_db():
    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()

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

    return render_template("dashboard.html",
                           total=total,
                           stats=stats,
                           data=data)

# -----------------------------
# Fonction envoi email
# -----------------------------
def envoyer_email(email, nom_enfant, nom_tuteur):
    message = MIMEText(
        f"Bonjour {nom_tuteur},\n\n"
        f"L'inscription de {nom_enfant} est confirmée.\n\n"
        "Merci."
    )
    message["Subject"] = "Confirmation d'inscription"
    message["From"] = "EMAIL_FROM"
    message["To"] = email

    mot_de_passe = os.environ.get("EMAIL_PASSWORD")

    serveur = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    serveur.login("jaddanih@gmail.com", mot_de_passe)
    serveur.send_message(message)
    serveur.quit()

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
    tel_tuteur = request.form['tel_tuteur'] from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
import csv
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

    # ✅ DROP pour forcer la recréation avec le bon schéma
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

    return render_template("dashboard.html",
                           total=total,
                           stats=stats,
                           data=data)

# -----------------------------
# Fonction envoi email
# -----------------------------
def envoyer_email(email, nom_enfant, nom_tuteur):
    # ✅ Adresse lue depuis la variable d'environnement
    email_from = os.environ.get("EMAIL_FROM")
    mot_de_passe = os.environ.get("EMAIL_PASSWORD")

    message = MIMEText(
        f"Bonjour {nom_tuteur},\n\n"
        f"L'inscription de {nom_enfant} est confirmée.\n\n"
        "Merci."
    )
    message["Subject"] = "Confirmation d'inscription"
    message["From"] = email_from
    message["To"] = email

    try:
        serveur = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        serveur.login(email_from, mot_de_passe)
        serveur.send_message(message)
        serveur.quit()
    except Exception as e:
        # ✅ L'email ne bloque plus l'inscription si ça échoue
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

        # ✅ Vérification correcte pour l'en-tête CSV
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


    nb_enfants = int(request.form.get("nb_enfants", 0))

    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()

    for i in range(1, nb_enfants + 1):
        nom_enfant = request.form.get(f"nom_enfant_{i}", "")
        prenom_enfant = request.form.get(f"prenom_enfant_{i}", "")
        allergies = request.form.get(f"allergies_enfant_{i}", "")

        # ✅ CORRECTION 1 : VALUES manquant + virgule entre la requête et les paramètres
        cursor.execute(
            "INSERT INTO inscriptions (nom, prenom, nom_tuteur, prenom_tuteur, email_tuteur, cours) VALUES (?, ?, ?, ?, ?, ?)",
            (nom_enfant, prenom_enfant, nom_tuteur, prenom_tuteur, email_tuteur, allergies)
        )

        # ✅ CORRECTION 2 : vérification correcte pour l'en-tête CSV
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

        # ✅ CORRECTION 3 : 3 paramètres au lieu de 2
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
    port = int(os.environ.get("PORT", 10000))  # ← lit le PORT de Render
    app.run(host="0.0.0.0", port=port)
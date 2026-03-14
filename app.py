from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "SECRET123"  # nécessaire pour session

# Admin sécurisé
admin_user = "admin"
admin_password = generate_password_hash("1234")

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
def envoyer_email(email, nom):
    message = MIMEText(f"Bonjour {nom}, votre inscription est confirmée.")
    message["Subject"] = "Confirmation inscription"
    message["From"] = "ton_email@gmail.com"
    message["To"] = email

    serveur = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    serveur.login("ton_email@gmail.com", "mot_de_passe")
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
    email_tuteur = request.form['email']
    nb_enfants = int(request.form["nb_enfants"])

    conn = sqlite3.connect("inscriptions.db")
    cursor = conn.cursor()

    # Boucle sur les enfants
    for i in range(1, nb_enfants + 1):
        nom = request.form[f"nom_{i}"]
        prenom = request.form[f"prenom_{i}"]
        cours = request.form[f"cours_{i}"]

        cursor.execute(
            "INSERT INTO inscriptions (nom, prenom, nom_tuteur, prenom_tuteur, email, cours) VALUES (?, ?, ?, ?, ?, ?)",
            (nom, prenom, nom_tuteur, prenom_tuteur, email_tuteur, cours)
        )

        # envoi email confirmation à chaque enfant
        envoyer_email(email_tuteur, nom)

    conn.commit()
    conn.close()

    return render_template("confirmation.html", nom_tuteur=nom_tuteur)

# -----------------------------
# Page admin simple
# -----------------------------
@app.route("/admin")
def admin():
    admin_required()

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
    admin_required()

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
    app.run(host="0.0.0.0", port=5000)
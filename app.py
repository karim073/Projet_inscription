from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
import csv

with open("data.csv") as f:
    data = list(csv.DictReader(f))
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
def envoyer_email(email, nom_enfant, nom_tuteur):
    message = MIMEText(
        f"Bonjour {nom_tuteur},\n\n"
        f"L'inscription de {nom_enfant} est confirmée.\n\n"
        "Merci."
    )
    message["Subject"] = "Confirmation d'inscription"
    message["From"] = "ton_email@gmail.com"
    message["To"] = email

    mot_de_passe = os.environ.get("EMAIL_PASSWORD")

    serveur = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    serveur.login("ton_email@gmail.com", mot_de_passe)
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
import csv

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

        # Pour SQLite, la colonne 'cours' on peut mettre les allergies ou laisser vide
        cursor.execute(
            "INSERT INTO inscriptions (nom, prenom, nom_tuteur, prenom_tuteur, email, cours) VALUES (?, ?, ?, ?, ?, ?)",
            (nom_enfant, prenom_enfant, nom_tuteur, prenom_tuteur, email_tuteur, allergies)
        )

        # CSV avec tous les champs
        with open("data.csv", "a", newline='', encoding='utf-8') as f:
            fieldnames = ["nom_tuteur", "prenom_tuteur", "email_tuteur", "tel_tuteur",
                          "nom_enfant", "prenom_enfant", "allergies"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
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

        # Appel envoyer_email avec les 2 paramètres que tu utilisais
        envoyer_email(email_tuteur, nom_enfant)

    conn.commit()
    conn.close()

    return render_template("confirmation.html", nom_tuteur=nom_tuteur)

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
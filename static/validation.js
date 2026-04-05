function validerFormulaire() {

    // ── Tuteur principal ──────────────────────────────────
    let nom = document.getElementById("nom_tuteur").value.trim();
    if (nom.length < 2) {
        alert("Le nom du tuteur est trop court.");
        return false;
    }

    let email = document.getElementById("email_tuteur").value.trim();
    if (!email.includes("@") || !email.includes(".")) {
        alert("Adresse courriel invalide.");
        return false;
    }

    let tel = document.getElementById("tel_tuteur").value.trim();
    if (tel.length < 10) {
        alert("Numéro de téléphone du tuteur invalide.");
        return false;
    }

    // ── 2e personne à contacter (obligatoire) ────────────
    let prenom2 = document.getElementById("prenom_contact2").value.trim();
    let nom2    = document.getElementById("nom_contact2").value.trim();
    let tel2    = document.getElementById("telephone_contact2").value.trim();

    if (prenom2.length < 2 || nom2.length < 2) {
        alert("Veuillez indiquer le prénom et le nom de la 2e personne à contacter.");
        return false;
    }
    if (tel2.length < 10) {
        alert("Le numéro de téléphone de la 2e personne à contacter est invalide.");
        return false;
    }

    // ── Enfants ───────────────────────────────────────────
    let nb = parseInt(document.getElementById("nb_enfants_hidden").value) || 1;

    for (let i = 1; i <= nb; i++) {
        let nomE    = document.getElementById(`nom_enfant_${i}`)?.value.trim();
        let prenomE = document.getElementById(`prenom_enfant_${i}`)?.value.trim();
        let ageE    = document.getElementById(`age_enfant_${i}`)?.value.trim();

        if (!nomE || nomE.length < 2) {
            alert(`Le nom de l'enfant ${i} est requis.`);
            return false;
        }
        if (!prenomE || prenomE.length < 2) {
            alert(`Le prénom de l'enfant ${i} est requis.`);
            return false;
        }
        if (!ageE || isNaN(ageE) || parseInt(ageE) < 3 || parseInt(ageE) > 18) {
            alert(`Veuillez entrer un âge valide (entre 3 et 18 ans) pour l'enfant ${i}.`);
            return false;
        }
    }

    // ── reCAPTCHA ─────────────────────────────────────────
    let recaptcha = grecaptcha.getResponse();
    if (!recaptcha || recaptcha.length === 0) {
        alert("Veuillez cocher la case reCAPTCHA avant d'envoyer.");
        return false;
    }

    return true;
}

// ── Génération dynamique des blocs enfants ────────────────
function genererFormulaires() {
    const nb        = parseInt(document.getElementById("nb_enfants").value);
    const container = document.getElementById("formulaires_enfants");
    const hidden    = document.getElementById("nb_enfants_hidden");
    hidden.value    = nb;
    container.innerHTML = "";

    for (let i = 1; i <= nb; i++) {
        const div = document.createElement("div");
        div.classList.add("form-group");
        div.id = `enfant-bloc-${i}`;
        div.innerHTML = `
            <h4>Enfant ${i}</h4>

            <label for="nom_enfant_${i}">Nom de l'enfant <span style="color:#c9a84c;">*</span></label>
            <input type="text" id="nom_enfant_${i}" name="nom_enfant_${i}"
                   placeholder="Nom de l'enfant" required>

            <label for="prenom_enfant_${i}">Prénom de l'enfant <span style="color:#c9a84c;">*</span></label>
            <input type="text" id="prenom_enfant_${i}" name="prenom_enfant_${i}"
                   placeholder="Prénom de l'enfant" required>

            <label for="age_enfant_${i}">Âge de l'enfant <span style="color:#c9a84c;">*</span></label>
            <input type="number" id="age_enfant_${i}" name="age_enfant_${i}"
                   placeholder="ex. 8" min="3" max="18" required>

            <label>
                <input type="checkbox" id="has_allergies_${i}" onchange="toggleAllergies(${i})">
                L'enfant a des allergies
            </label>
            <div id="allergies_container_${i}" style="display:none; margin-top:10px;">
                <label for="allergies_enfant_${i}">Allergies éventuelles</label>
                <input type="text" id="allergies_enfant_${i}" name="allergies_enfant_${i}"
                       placeholder="Liste des allergies">
            </div>
        `;
        container.appendChild(div);
    }
}

function toggleAllergies(i) {
    const checkbox  = document.getElementById(`has_allergies_${i}`);
    const container = document.getElementById(`allergies_container_${i}`);
    container.style.display = checkbox.checked ? 'block' : 'none';
}

window.onload = function () {
    genererFormulaires();
    document.getElementById("nb_enfants_hidden").value =
        document.getElementById("nb_enfants").value;
};

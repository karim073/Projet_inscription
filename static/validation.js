function validerFormulaire() {

    // Vérification du nom du tuteur
    let nom = document.getElementById("nom_tuteur").value;
    if (nom.length < 2) {
        alert("Nom du tuteur trop court.");
        return false;
    }

    // Vérification de l'email du tuteur
    let email = document.getElementById("email_tuteur").value;
    if (!email.includes("@")) {
        alert("Adresse email invalide.");
        return false;
    }

    // ✅ Vérification reCAPTCHA
    let recaptcha = grecaptcha.getResponse();
    if (!recaptcha || recaptcha.length === 0) {
        alert("Veuillez cocher la case reCAPTCHA avant d'envoyer.");
        return false;
    }

    return true;
}

function genererFormulaires() {
    const nb = parseInt(document.getElementById("nb_enfants").value);
    const container = document.getElementById("formulaires_enfants");
    const hiddenField = document.getElementById("nb_enfants_hidden");

    hiddenField.value = nb;
    container.innerHTML = "";

    for (let i = 1; i <= nb; i++) {
        const div = document.createElement("div");
        div.classList.add("form-group");

        div.innerHTML = `
            <h4>Enfant ${i}</h4>

            <label for="nom_enfant_${i}">Nom de l'enfant</label>
            <input type="text" id="nom_enfant_${i}" name="nom_enfant_${i}" placeholder="Nom de l'enfant" required>

            <label for="prenom_enfant_${i}">Prénom de l'enfant</label>
            <input type="text" id="prenom_enfant_${i}" name="prenom_enfant_${i}" placeholder="Prénom de l'enfant" required>

            <label for="cours_enfant_${i}">Niveau du cours</label>
            <select id="cours_enfant_${i}" name="cours_enfant_${i}" required>
                <option value="" disabled selected>-- Choisir un niveau --</option>
                <option value="Élémentaire">Élémentaire</option>
                <option value="Niveau 1">Niveau 1</option>
                <option value="Niveau 2">Niveau 2</option>
                <option value="Niveau 3">Niveau 3</option>
            </select>

            <label>
                <input type="checkbox" id="has_allergies_${i}" onchange="toggleAllergies(${i})">
                L'enfant a des allergies
            </label>

            <div id="allergies_container_${i}" style="display:none; margin-top:10px;">
                <label for="allergies_enfant_${i}">Allergies éventuelles</label>
                <input type="text" id="allergies_enfant_${i}" name="allergies_enfant_${i}" placeholder="Liste des allergies">
            </div>
        `;

        container.appendChild(div);
    }
}

function toggleAllergies(i) {
    const checkbox = document.getElementById(`has_allergies_${i}`);
    const container = document.getElementById(`allergies_container_${i}`);
    container.style.display = checkbox.checked ? 'block' : 'none';
}

window.onload = function () {
    genererFormulaires();
    document.getElementById("nb_enfants_hidden").value =
        document.getElementById("nb_enfants").value;
};
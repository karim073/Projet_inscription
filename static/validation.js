function validerFormulaire(){

let nom = document.forms["formInscription"]["nom"].value;
let email = document.forms["formInscription"]["email"].value;

if(nom.length < 2){
    alert("Nom trop court");
    return false;
}

if(!email.includes("@")){
    alert("Email invalide");
    return false;
}

return true;
}
function genererFormulaires() {

let nb = document.getElementById("nb_enfants").value;

let zone = document.getElementById("formulaires_enfants");

zone.innerHTML = "";

for(let i = 1; i <= nb; i++){

zone.innerHTML += `
<h3>Enfant ${i}</h3>

<input type="text" name="nom_${i}" placeholder="Nom de l'enfant ${i}" required>

<input type="text" name="prenom_${i}" placeholder="Prénom de l'enfant ${i}" required>

<select name="cours_${i}">
<option>Python</option>
<option>Développement Web</option>
<option>Data Science</option>
</select>

<br><br>
`;
}
}
function genererFormulaires() {
    let nb = document.getElementById("nb_enfants").value;
    
    // Mettre à jour le champ caché
    document.getElementById("nb_enfants_hidden").value = nb;

    let zone = document.getElementById("formulaires_enfants");
    zone.innerHTML = "";

    for (let i = 1; i <= nb; i++) {
        zone.innerHTML += `
        <h3>Enfant ${i}</h3>
        <input type="text" name="nom_${i}" placeholder="Nom de l'enfant ${i}" required>
        <input type="text" name="prenom_${i}" placeholder="Prénom de l'enfant ${i}" required>
        <select name="cours_${i}">
            <option>Python</option>
            <option>Développement Web</option>
            <option>Data Science</option>
        </select>
        <br><br>
        `;
    }
}
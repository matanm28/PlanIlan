let blockedTimesForm = document.querySelectorAll("#formset")
let container = document.querySelector(".form")
let addButton = document.querySelector("#add-form")
let totalForms = document.querySelector("#id_form-TOTAL_FORMS")

let formNum = blockedTimesForm.length - 1
addButton.addEventListener('click', addForm)

function addForm(e) {
    e.preventDefault()

    let newForm = blockedTimesForm[0].cloneNode(true)
    let formRegex = RegExp(`form-(\\d){1}-`, 'g')

    formNum++
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`)
    container.insertBefore(newForm, addButton)

    totalForms.setAttribute('value', `${formNum + 1}`)
}

function deleteForm(btn) {
    btn.parentElement.remove();
    formNum--;
    let count = 0;
    for (let form of blockedTimesForm) {
        const formRegex = RegExp(`form-(\\d){1}-`, 'g');
        form.innerHTML = form.innerHTML.replace(formRegex, `form-${count++}-`)
    }
    totalForms.setAttribute('value', `${formNum + 1}`);
}
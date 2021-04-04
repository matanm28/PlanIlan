const mandatory_courses = []
const elective_courses = []

function create_groups() {
    let x = document.getElementById("selected-option");
    let i = x.selectedIndex;
    let selected_option = x.options[i].text;
    let name = document.getElementById("group-name")
    let b = document.createElement('button');
    b.setAttribute('class', 'btn btn-link');
    b.textContent = name.value + '-' + selected_option;
    b.setAttribute('id', 'btn-group_' + b.textContent)
    let wrapper = document.getElementById("wrapper-div");
    wrapper.appendChild(b);
    let remove = document.createElement('button');
    remove.setAttribute('class', 'fas fa-trash close-btn-groups')
    remove.setAttribute('onClick', 'removeGroup(this)')
    remove.setAttribute('id', 'remove-group_' + b.textContent)
    wrapper.appendChild(remove)
}

function removeGroup(item) {
    let group_name = item.id.split("_")[1]
    let button_group = document.getElementById("btn-group_" + group_name)
    button_group.remove()
    item.remove()
}

// TODO: not working
// Filtering after picking from list
let dep_drop = document.getElementById("select-dep");
$(dep_drop).change((event) => {
    let data = {
        'department': dep_drop.options[dep_drop.selectedIndex].value,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/timetable',
        type: 'GET',
        data: data,
        success: function (data) {
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
});

const formValues = JSON.parse(localStorage.getItem('formValues')) || {};
const $checkboxes = $("#course-data :checkbox");
const $button = $(document.getElementById("pick-all"));

function allChecked() {
    return $checkboxes.length === $checkboxes.filter(":checked").length;
}

function updateButtonStatus() {
    $button.text(allChecked() ? "Uncheck all" : "Check all");
}

function handleButtonClick() {
    $checkboxes.prop("checked", !allChecked())
}

function updateStorage() {
    $checkboxes.each(function () {
        formValues[this.id] = this.checked;
    });

    formValues["buttonText"] = $button.text();
    localStorage.setItem("formValues", JSON.stringify(formValues));
}

$button.on("click", function () {
    console.log("HHH")
    handleButtonClick();
    updateButtonStatus();
    updateStorage();
});

$checkboxes.on("change", function () {
    updateButtonStatus();
    updateStorage();
});

// On page load
$.each(formValues, function (key, value) {
    $("#" + key).prop('checked', value);
});

$button.text(formValues["buttonText"]);
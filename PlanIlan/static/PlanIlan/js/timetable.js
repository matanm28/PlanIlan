const mandatory_courses = []
const elective_courses = []
const formValues = JSON.parse(sessionStorage.getItem('formValues')) || {};


function create_groups() {
    let x = document.getElementById("selected-option");
    let i = x.selectedIndex;
    let selected_option = x.options[i].text;
    let wrapper = document.getElementById("wrapper-div");
    let name = document.getElementById("group-name");
    let div_name = name.value + '-' + selected_option;
    let div_result = document.createElement('div');
    div_result.setAttribute('id', "div-group_" + div_name);
    let title = "<lable>" + div_name + "</lable>";
    div_result.innerHTML += title;
    let remove = '<button class="fas fa-trash close-btn-groups" onclick="removeGroup(this)" id="remove-group_'
        + div_name +'"></button>'
    div_result.innerHTML += remove;
    div_result.innerHTML += '<br><button class="button btn-primary">הוסף קורסים</button>';
    let modal = document.querySelector(".modal-content");
    let this_div_modal = modal.cloneNode(true);
    div_result.innerHTML += this_div_modal.setAttribute('id', 'modal_' + div_name);
    wrapper.append(div_result);
}

function removeGroup(item) {
    let group_name = item.id.split("_")[1]
    let div_group = document.getElementById("div-group_" + group_name)
    div_group.remove()
    item.remove()
}


const $checkboxes = $("#course-data :checkbox");
const $button = $(document.getElementById("pick-all"));

function allChecked() {
    return $checkboxes.length === $checkboxes.filter(":checked").length;
}

function handleButtonClick() {
    $checkboxes.prop("checked", !allChecked())
}

function updateStorage() {
    $checkboxes.each(function () {
        formValues[this.id] = this.checked;
    });
    sessionStorage.setItem("formValues", JSON.stringify(formValues));
}

$button.on("click", function () {
    handleButtonClick();
    updateStorage();
});

$checkboxes.on("change", function () {
    updateStorage();
});

// On page load
window.onload = function () {
    //window.location.href += "?page=" + formValues["page_number"];
    let selectedItem = formValues["selected-dep"];
    let dep_drop = document.getElementById("select-dep");
    $.each(formValues, function (key, value) {
        $("#" + key).prop('checked', value);
    });
    if (selectedItem) {
        dep_drop.value = selectedItem;
    }
    let data = {
        'department': selectedItem,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/timetable',
        type: 'GET',
        data: data,
        success: function (data) {
            const course_table = $(data).filter('#course-table');
            $('#course-table').replaceWith(course_table);
        },
        error: function (error) {
            alert("בעיה בטעינת הטבלה");
        }
    });
    return false;
}

// $(function () {
//     let course_table = formValues["page_number"];
//     let selectedItem = formValues["selected-dep"];
//     let dep_drop = document.getElementById("select-dep");
//
//     if (selectedItem) {
//         dep_drop.value = selectedItem;
//     }
//     if (course_table) {
//         $('#course-table').html(course_table);
//     }
// });

// TODO: not working
// Filtering after picking from list
function DepChange() {
    let dep_drop = document.getElementById("select-dep");
    formValues["selected-dep"] = dep_drop.options[dep_drop.selectedIndex].value;
    let data = {
        'department': dep_drop.options[dep_drop.selectedIndex].value,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/timetable',
        type: 'GET',
        data: data,
        success: function (data) {
            const course_table = $(data).filter('#course-table');
            $('#course-table').replaceWith(course_table);
            formValues['page_number'] = $(data).filter('#current-page');
            sessionStorage.setItem("formValues", JSON.stringify(formValues));
        },
        error: function (error) {
            alert("בעיה בטעינת הטבלה");
        }
    });
    return false;
}
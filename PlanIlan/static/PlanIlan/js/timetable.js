const mandatory_courses = []
const elective_courses = []
const formValues = JSON.parse(sessionStorage.getItem('formValues')) || {};

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
    let list_course = document.createElement('ol');
    $checkboxes.filter(":checked").forEach(checked_item => {
        let li = document.createElement('li');
        li.setAttribute('id', checked_item.id);
        li.appendChild(checked_item);
    })
    wrapper.appendChild(list_course)
    if (selected_option === 'חובה') {
        mandatory_courses.push($checkboxes.filter(":checked"));
    } else {
        elective_courses.push($checkboxes.filter(":checked"));
    }
}

function removeGroup(item) {
    let group_name = item.id.split("_")[1]
    let button_group = document.getElementById("btn-group_" + group_name)
    button_group.remove()
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
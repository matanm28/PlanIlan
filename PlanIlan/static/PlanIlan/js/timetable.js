const mandatory_courses = []
const elective_courses = []

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
        + div_name + '"></button>'
    div_result.innerHTML += remove;
    let create_course_btn = '<br><button class="button btn-primary" id="btn-modal_' + div_name +
        '" onclick="openModal(this)">הוסף קורסים</button>';
    div_result.innerHTML += create_course_btn;
    wrapper.append(div_result);
}

let modal = document.querySelector('.modal');
let span = document.getElementsByClassName("close")[0];

function openModal() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

function removeGroup(item) {
    let group_name = item.id.split("_")[1]
    let div_group = document.getElementById("div-group_" + group_name)
    div_group.remove()
    item.remove()
}


const $checkboxes = $("#course-data :checkbox");
const $button = $(document.getElementById("pick-all"));

let values = $('#semester').val();
// TODO: not working
// Filtering after picking from list
function DepChange() {
    let dep_drop = document.getElementById("select-dep");
    let data = {
        'department': dep_drop.options[dep_drop.selectedIndex].value,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/timetable',
        type: 'GET',
        data: data,
        success: function (data) {
            let arr_from_json = JSON.parse(data.json_course_list);
            let options_div = document.getElementById("options");
            options_div.innerHTML = '';
            for (let i = 0; i < arr_from_json.length; i++) {
                let line_checkbox = '<input type="checkbox" id="check-course_' + arr_from_json[i]["pk"] + '" value="' + data.json_course_names[i] + '" onclick="showSaveButton(this)">'
                let line_lable = '<label for="' + arr_from_json[i]["pk"] + '">' + data.json_course_names[i] + '</label><br>'
                options_div.innerHTML += line_checkbox
                options_div.innerHTML += line_lable
            }
        },
        error: function (error) {
            alert("בעיה בטעינת הטבלה");
        }
    });
    return false;
}

function showSaveButton(checkbox) {
    let buttn = document.getElementById("submit_prog");
    if (checkbox.checked === true) {
        buttn.style.display = "block";
    } else {
        buttn.style.display = "none";
    }
}
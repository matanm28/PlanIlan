const mandatory_courses = []
const elective_courses = []
// Because used by 2 functions
let wait_msg = document.getElementById("wait-msg");

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

let values = $('#semester').val();
// TODO: not working
// Filtering after picking from list
function DepChange() {
    wait_msg.style.display = "block";
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
            wait_msg.style.display = "none";
            let options_div = document.getElementById("options");
            options_div.innerHTML = '';
            let lessons_from_json = JSON.parse(data.json_lesson_list);
            let courses_from_json = JSON.parse(data.json_course_list);
            let teacher_from_json = JSON.parse(data.json_teacher_list);
            let session_time_from_json = JSON.parse(data.json_session_list);
            for (let i = 0; i < courses_from_json.length; i++) {
                let course_line = '<button id="course_' + courses_from_json[i]["pk"] + '" type="button" ' +
                    'class="collapsible" onclick="showCollapsible(this)">' + courses_from_json[i]["fields"]["name"] + '</button>'
                let div_lessons = document.createElement('div');
                div_lessons.setAttribute('class', 'content-coll')
                for (let j = 0; j < lessons_from_json.length; j++) {
                    if (lessons_from_json[j]["pk"].split("_")[0] === courses_from_json[i]["pk"]) {
                        let line_checkbox = '<input type="checkbox" id="check-lesson_' +
                            lessons_from_json[j]["pk"] + '" value="' + lessons_from_json[j]["fields"]["teachers"] + '" onclick="showSaveButton(this)">'
                        let line_lable = '<label for="check-lesson_' + lessons_from_json[j]["pk"] + '">' +
                            createLine(teacher_from_json, lessons_from_json[j], session_time_from_json) + '</label><br>'
                        div_lessons.innerHTML += line_checkbox
                        div_lessons.innerHTML += line_lable
                    }
                }
                options_div.innerHTML += course_line
                options_div.append(div_lessons)
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
        let checked_boxes = $('#options input:checked');
        if (checked_boxes.length === 0) {
            buttn.style.display = "none";
        }
    }
}

function showCollapsible(coll) {
    coll.classList.toggle("active-coll");
    var content = coll.nextElementSibling;
    if (content.style.display === "block") {
        content.style.display = "none";
    } else {
        content.style.display = "block";
    }
}

function createLine(teachers, lesson, session_times) {
    let teacher_name = "";
    let day = "";
    let semester = "";
    let start_hour = "";
    let end_hour = "";
    Object.keys(teachers).forEach(function (key) {
        let value = teachers[key];
        if (lesson["fields"]["teachers"].includes(value["pk"]) === true) {
            teacher_name += value["fields"]["name"];
        }
    });
    Object.keys(session_times).forEach(function (key) {
        let DAYS = [null, 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי']
        let SEMESTERS = [null, 'סמסטר א', 'סמסטר ב', 'סמסטר ק', 'שנתי']
        let value = session_times[key];
        if (lesson["fields"]["session_times"].includes(value["pk"]) === true) {
            day += DAYS[parseInt(value["fields"]["day"])];
            semester += SEMESTERS[parseInt(value["fields"]["semester"])];
            start_hour += value["fields"]["start_time"];
            end_hour += value["fields"]["end_time"];
        }
    });
    return "מרצה/מתרגל:" + teacher_name + ", " + semester + ",יום " + day + ",שעת התחלה: " + start_hour + ",שעת סיום: " + end_hour;
}
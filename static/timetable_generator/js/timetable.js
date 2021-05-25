const mandatory_courses = []
const elective_courses = []
// Because used by 2 functions
let wait_msg = document.getElementById("wait-msg");
// For accessing the lessons from everywhere
let lessons_from_json = "";
let courses_from_json = "";
let teacher_from_json = "";
let session_time_from_json = "";
let name = document.getElementById("group-name");
let x = document.getElementById("selected-option");
let buttn = document.getElementById("submit_prog");

function create_groups() {
    let i = x.selectedIndex;
    let selected_option = x.options[i].text;
    let wrapper = document.getElementById("wrapper-div");
    let div_name = name.value + '-' + selected_option;
    let div_result = document.createElement('div');
    div_result.setAttribute('id', "div-group_" + div_name);
    let title = "<lable>" + div_name + "</lable>";
    div_result.innerHTML += title;
    let remove = '<button class="fas fa-trash close-btn-groups" onclick="removeGroup(this)" id="remove-group_'
        + div_name + '"></button>'
    div_result.innerHTML += remove;
    let selected_courses = document.createElement('ul');
    selected_courses.setAttribute('id', "selected-courses_" + div_name);
    div_result.append(selected_courses)
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
            buttn.style.display = "none";
            wait_msg.style.display = "none";
            let options_div = document.getElementById("options");
            options_div.innerHTML = '';
            lessons_from_json = JSON.parse(data.json_lesson_list);
            courses_from_json = JSON.parse(data.json_course_list);
            teacher_from_json = JSON.parse(data.json_teacher_list);
            session_time_from_json = JSON.parse(data.json_session_list);
            for (let i = 0; i < courses_from_json.length; i++) {
                let course_line = '<button id="course_' + courses_from_json[i]["pk"] + '" type="button" ' +
                    'class="collapsible" onclick="showCollapsible(this)">' + courses_from_json[i]["fields"]["name"] + '</button>'
                let div_lessons = document.createElement('div');
                div_lessons.setAttribute('class', 'content-coll')
                for (let j = 0; j < lessons_from_json.length; j++) {
                    if (lessons_from_json[j]["pk"].split("_")[0] === courses_from_json[i]["pk"]) {
                        let checkbox_info = createLine(teacher_from_json, lessons_from_json[j], session_time_from_json)
                        let line_checkbox = '<input type="checkbox" id="check-lesson_' +
                            lessons_from_json[j]["pk"] + '" value="' + lessons_from_json[j]["pk"] + '" onclick="showSaveButton(this)">'
                        let line_lable = '<label for="check-lesson_' + lessons_from_json[j]["pk"] + '">' +
                            checkbox_info + '</label><br>'
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

let teacher_name = "";
let day = "";
let semester = "";
let start_hour = "";
let end_hour = "";

function createLine(teachers, lesson, session_times) {
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

$('#submit_prog').on("click", function () {
    modal.style.display = "none";
    let i = x.selectedIndex;
    let selected_option = x.options[i].text;
    let checked_boxes = $('#options input:checked');
    Array.from(checked_boxes).forEach(function (checkbox) {
        let lesson_pk = checkbox.value;
        if (mandatory_courses.includes(lesson_pk.split("_")[0]) || elective_courses.includes(lesson_pk.split("_")[0])) {
            return;
        }
        if (selected_option === "חובה") {
            mandatory_courses.push(lesson_pk.split("_")[0])
        } else {
            elective_courses.push(lesson_pk.split("_")[0])
        }
    });
    addLessonsToDiv(selected_option);
});

function addLessonsToDiv(selected_option) {
    let group_name = name.value + '-' + selected_option;
    let list = document.getElementById("selected-courses_" + group_name);
    list.innerHTML = "";
    if (selected_option === "חובה") {
        mandatory_courses.forEach(function (course) {
            let list_line = '<li>'
            Object.keys(courses_from_json).forEach(function (key) {
                let value = courses_from_json[key];
                if (course === value["pk"]) {
                    list_line += value["fields"]["name"]
                }
            });
            list_line += '</li>'
            list.innerHTML += list_line;
        });
    } else {
        elective_courses.forEach(function (course) {

        });
    }
}
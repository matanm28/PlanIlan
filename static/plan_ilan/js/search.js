function display_teacher_filter() {
    document.getElementById('course_filter').style.display = "none";
    document.getElementById('course_button').classList.remove('clicked');
    document.getElementById('teacher_filter').style.display = "block";
    document.getElementById('teacher_button').classList.add('clicked');
}

function display_course_filter() {
    document.getElementById('teacher_filter').style.display = "none";
    document.getElementById('teacher_button').classList.remove('clicked');
    document.getElementById('course_filter').style.display = "block";
    document.getElementById('course_button').classList.add('clicked');
}

/* Set the width of the side navigation to 250px */
function openSearchBox() {
    document.getElementById("search_box").style.width = "25%";
    document.getElementById("results").style.marginRight = "25%";
    document.getElementById("results").style.width = "75%";
    document.getElementById("open_search_box").style.display = "none";
    const results = document.getElementsByClassName("resize-box");
    for (let i = 0; i < results.length; i++) {
        results[i].style.width = "100%";
    }
}

/* Set the width of the side navigation to 0 */
function closeSearchBox() {
    document.getElementById("search_box").style.width = "0";
    document.getElementById("results").style.marginRight = "0";
    document.getElementById("results").style.width = "100%";
    document.getElementById("open_search_box").style.display = "block";
    const results = document.getElementsByClassName("resize-box");
    for (let i = 0; i < results.length; i++) {
        results[i].style.width = "98%";
    }
}

function chosenElement(id, type) {
    let spinner = document.getElementById("spinner")
    spinner.style.display = "block";
    let former_chosen_element = document.getElementsByClassName("shown");
    if (former_chosen_element !== undefined && former_chosen_element.length > 0) {
        former_chosen_element = former_chosen_element[0];
        former_chosen_element.classList.remove("shown");
        former_chosen_element.style.display = "none";
    }
    const code = id.split("_")[2];
    let data = {
        'code': code,
        'type': type,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/search',
        type: 'GET',
        data: data,
        success: function (data) {
            if (type === 'c') {
                addCourseDetails(code, data)
            } else {
                addTeacherDetails(code, data)
            }
            spinner.style.display = "none";
            const chosen_element = document.getElementById(id);
            chosen_element.classList.add("shown");
            chosen_element.style.display = "block";
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
}

function addCourseDetails(code, data) {
    let course_data = JSON.parse(data.chosen_course);
    let types = JSON.parse(data.lesson_types);
    let staff = JSON.parse(data.staff);
    let lessons = JSON.parse(data.lessons);
    let lesson_times = JSON.parse(data.lessons_times);
    let link = course_data[0]["fields"]["syllabus_link"]
    staff = get_field(staff, 'name');
    types = get_field(types, 'label');
    lesson_times = get_times_details(lessons, lesson_times, data.session_dict);
    // adding details
    document.getElementById("name_" + code).innerHTML = course_data[0]["fields"]["name"]
    document.getElementById("code_" + code).innerHTML = "<i>קוד: </i>" + code
    document.getElementById("type_" + code).innerHTML = "<i>סוג מפגש: </i>" + types
    document.getElementById("staff_" + code).innerHTML = "<i>סגל: </i>" + staff
    document.getElementById("times_" + code).innerHTML = "<i>זמנים: </i>" + lesson_times
    if (link != null) {
        const txt = "לצפייה בסילבוס";
        document.getElementById("link_" + code).innerHTML = txt.link(link);
    }
}

function addTeacherDetails(id, data) {
    let title_and_name = data.teacher['name'];
    let faculties = data.teacher['faculties'];
    let departments = data.teacher['departments'];
    let link = data.teacher['url'];
    // adding details
    document.getElementById("name_" + id).innerHTML = title_and_name
    if (faculties.length > 1) {
        document.getElementById("faculty_" + id).innerHTML = "<i>פקולטות: </i>" + faculties.toString()
    }
    if (faculties.length === 1) {
        document.getElementById("faculty_" + id).innerHTML = "<i>פקולטה: </i>" + faculties.toString()
    }
    if (departments.length > 1) {
        document.getElementById("department_" + id).innerHTML = "<i>מחלקות: </i>" + departments.toString()
    }
    if (departments.length === 1) {
        document.getElementById("department_" + id).innerHTML = "<i>מחלקה: </i>" + departments.toString()
    }
    if (link != null) {
        const txt = "לאתר המורה";
        document.getElementById("link_" + id).innerHTML = txt.link(link);
    }
}

function get_field(arr, f) {
    let staff_names = []
    for (let i = 0; i < arr.length; i++) {
        staff_names.push((arr[i].fields)[f])
    }
    return staff_names.toString()
}

function get_times_details(lessons, lessons_times, session_dict) {
    let details = []
    for (let i = 0; i < lessons.length; i++) {
        for (let j = 0; j < lessons_times.length; j++) {
            let pk = lessons_times[j]['pk'];
            if (pk === lessons[i].fields['session_times'][0]) {
                let num = lessons[i].fields['group'];
                let time = session_dict[pk];
                details.push("קבוצה " + num + " - " + time);
            }
        }
    }
    return details.toString()
}


$(function () {
    $("#courses_results").resizable();
    $("#chosen_elements").resizable();
});

// $(document).ready(function () {
//   $("#courses_result").resizable({
//     containment: 'parent',
//     handles: 'e'
//   });
// });
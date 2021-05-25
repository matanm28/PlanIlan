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

function chosenElement(id) {
    let former_chosen_course = document.getElementsByClassName("shown");
    if (former_chosen_course !== undefined && former_chosen_course.length > 0) {
        former_chosen_course = former_chosen_course[0];
        former_chosen_course.classList.remove("shown");
        former_chosen_course.style.display = "none";
    }
    const course_code = id.split("_")[2];
    let data = {
        'code': course_code,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/search',
        type: 'GET',
        data: data,
        success: function (data) {
            let course_data = JSON.parse(data.chosen_course);
            let exams = JSON.parse(data.exams);
            let times = JSON.parse(data.lesson_times);
            let types = JSON.parse(data.lesson_types);
            let staff = JSON.parse(data.staff);
            document.getElementById("name_" + course_code).value = course_data[0]["fields"]["name"]
            document.getElementById("code_" + course_code).value = course_code
            const chosen_course = document.getElementById(id);
            chosen_course.classList.add("shown");
            chosen_course.style.display = "block";
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
}

$(function () {
    $("#courses_result").resizable();
    $("#chosen_element").resizable();
});
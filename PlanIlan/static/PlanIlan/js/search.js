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
    document.getElementById("results").style.marginLeft = "25%";
    document.getElementById("results").style.width = "75%";
    document.getElementById("search_box").style.width = "25%";
    document.getElementById("open_search_box").style.display = "none";
    const results = document.getElementsByClassName("resize-box");
    for (let i = 0; i < results.length; i++) {
        results[i].style.width = "75%";
    }
}

/* Set the width of the side navigation to 0 */
function closeSearchBox() {
    document.getElementById("search_box").style.width = "0";
    document.getElementById("open_search_box").style.display = "block";
    document.getElementById("results").style.marginLeft = "0";
    const results = document.getElementsByClassName("resize-box");
    for (let i = 0; i < results.length; i++) {
        results[i].style.width = "90%";
    }
}
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
    document.getElementById("search_box").style.width = "250px";
    document.getElementById("results").style.marginLeft = "250px";
    document.getElementById("open_search_box").style.display = "none";
}

/* Set the width of the side navigation to 0 */
function closeSearchBox() {
    document.getElementById("search_box").style.width = "0";
    document.getElementById("open_search_box").style.display = "block";
    document.getElementById("results").style.marginLeft = "0";
}
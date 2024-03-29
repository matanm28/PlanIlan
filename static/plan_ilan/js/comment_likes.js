function changeHeart(pressed) {
    pressed.classList.toggle('red');
    let type = pressed.id.split("_")[1]
    let post_id = pressed.id.split("_")[2]
    let data = {
        'PostID': post_id,
        'csrfmiddlewaretoken': csrftoken,
        'to_add': -1,
        'type': type
    };
    if (pressed.classList.contains('red')) {
        data['to_add'] = 1
    }
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: data,
        success: function (data) {
            let amount_of_likes = JSON.parse(data.amount_likes);
            document.getElementById("amount_" + post_id).innerText = amount_of_likes + " אנשים אהבו את זה"
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
}

window.onload = function () {
    let data = {
        'load_likes': true,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: data,
        success: function (data) {
            let likes_from_json = JSON.parse(data.json_likes_list);
            for (let i = 0; i < likes_from_json.length; i++) {
                let post = document.getElementById("heart_course_" + likes_from_json[i]["fields"]["review"]);
                if (post === null) {
                    post = document.getElementById("heart_teacher_" + likes_from_json[i]["fields"]["review"]);
                }
                if (post !== null) {
                    post.classList.add('red');
                }
            }
        },
        error: function (error) {

        }
    });
    return false;
}


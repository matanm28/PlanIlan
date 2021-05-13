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
        url: '/',
        type: 'POST',
        data: data,
        success: function (data) {
            // if (event.target.classList.contains('red')) {
            //     p.parentNode.querySelector("[id^=amount_]").stepUp(1);
            // } else {
            //     p.parentNode.querySelector("[id^=amount_]").stepUp(-1);
            // }
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
}

window.onload = function () {
    $.ajax({
        url: '/',
        type: 'GET',
        success: function (data) {
            let likes_from_json = JSON.parse(data.json_likes_list);
            for (let i = 0; i < likes_from_json.length; i++) {
                let post = document.getElementById("heart_course_" + likes_from_json[i]["fields"]["review"]);
                post.classList.add('red');
            }
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
}


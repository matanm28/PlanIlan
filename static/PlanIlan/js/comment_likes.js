$(document.querySelectorAll('.fa-heart')).click((event) => {
    event.target.classList.toggle('red');
    const p = event.target.parentNode;
    let id = $(p).data("id");
    let data = {
        'PostID': id,
        'csrfmiddlewaretoken': csrftoken,
        'to_add': -1
    };
    if (event.target.classList.contains('red')) {
        data['to_add'] = 1
    }
    $.ajax({
        url: '/',
        type: 'POST',
        data: data,
        success: function (data) {
            if (event.target.classList.contains('red')) {
                p.parentNode.querySelector("[id^=amount_]").stepUp(1);
            } else {
                p.parentNode.querySelector("[id^=amount_]").stepUp(-1);
            }
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
});



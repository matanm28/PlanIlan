$(document.querySelectorAll('.fa-heart')).click((event) => {
    event.target.classList.toggle('red');
    const p = event.target.parentNode;
    let id = $(p).data("id");
    let data = {
        'PostID': id,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/',
        type: 'POST',
        data: data,
        success: function (data) {
            p.parentNode.querySelector("[id^=amount_]").stepUp(1);
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
});



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

(function () {
    const heart = document.getElementById('heart');
    heart.addEventListener('click', function () {
        heart.classList.toggle('red');
    });
})();


$("[id^=form_]").click(function () {
    let id = $(this).data("id");
    data = {
        'PostID': id,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/',
        type: 'POST',
        data: data,
        success: function (data) {
            let amount = document.querySelector("[id^=amount_]");
            amount.innerText += 1
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
});


var star_value = 0

const handleStarSelect = (size, children) => {
    for (let i = 0; i < children.length; i++) {
        if (i <= size) {
            children[i].classList.add('checked')
        } else {
            children[i].classList.remove('checked')
        }
    }
}
const handleSelect = (selection, children) => {
    switch (selection) {
        case 'first-star': {
            star_value = 1
            handleStarSelect(1, children)
            return
        }
        case 'second-star': {
            star_value = 2
            handleStarSelect(2, children)
            return
        }
        case 'third-star': {
            star_value = 3
            handleStarSelect(3, children)
            return
        }
        case 'fourth-star': {
            star_value = 4
            handleStarSelect(4, children)
            return
        }
        case 'fifth-star': {
            star_value = 5
            handleStarSelect(5, children)
            return
        }
    }

}

$(document.querySelectorAll('.fa-star')).hover((event) => {
    const parent = event.target.parentNode;
    const children = parent.children
    const location = event.target.id.split("_")[0];
    handleSelect(location, children)
});

$(document.querySelectorAll('.fa-star')).click((event) => {
    let id = $(event.target).data("id");
    console.log(star_value)
    let data = {
        'rate_number': star_value,
        'Rating_course_ID': id,
        'csrfmiddlewaretoken': csrftoken,
    };
    $.ajax({
        url: '/',
        type: 'POST',
        data: data,
        success: function (data) {
            alert('successfully rated');
        },
        error: function (error) {
            alert('error; ' + eval(error));
        }
    });
    return false;
});
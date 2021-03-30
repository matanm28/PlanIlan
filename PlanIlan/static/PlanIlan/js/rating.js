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
            handleStarSelect(1, children)
            return
        }
        case 'second-star': {
            handleStarSelect(2, children)
            return
        }
        case 'third-star': {
            handleStarSelect(3, children)
            return
        }
        case 'fourth-star': {
            handleStarSelect(4, children)
            return
        }
        case 'fifth-star': {
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
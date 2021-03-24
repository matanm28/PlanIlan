// get all the starts
const one = document.getElementById('first-star')
const two = document.getElementById('second-star')
const three = document.getElementById('third-star')
const four = document.getElementById('fourth-star')
const five = document.getElementById('fifth-star')
const arr = [one, two, three, four, five]
const form = document.querySelector('.rate-form')
const confirmBox = document.getElementById('confirm-box')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

const handleStarSelect = (size) => {
    const children = form.children
    for (let i = 0; i < children.length; i++) {
        if (i <= size) {
            children[i].classList.add('checked')
        } else {
            children[i].classList.remove('checked')
        }
    }
}
const handleSelect = (selection) => {
    switch (selection) {
        case 'first-star': {
            handleStarSelect(1)
            return
        }
        case 'second-star': {
            handleStarSelect(2)
            return
        }
        case 'third-star': {
            handleStarSelect(3)
            return
        }
        case 'fourth-star': {
            handleStarSelect(4)
            return
        }
        case 'fifth-star': {
            handleStarSelect(5)
            return
        }
    }

}
arr.forEach(item => item.addEventListener('mouseover', (event) => {
    handleSelect(event.target.id)
}))
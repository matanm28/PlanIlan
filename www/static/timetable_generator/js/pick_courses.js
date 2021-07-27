const leftSliderText = document.getElementById('left');
const rightSliderText = document.getElementById('right');

$(document).ready(function () {
    const sliderFormatter = (value) => {
        if (value[1]) {
            const [left, right] = value;
            return `לא פחות מ-${left} נקודות ולא יותר מ- ${right} נקודות `
        }
        return value;
    }

    let slider = new Slider('#elective_points_range',
        {
            id: "points_slider",
            min: 0,
            max: 50,
            range: true,
            reversed: true,
            formatter: sliderFormatter
        });
    slider.on("change", value => {
        const [left, right] = value.newValue;
        leftSliderText.innerHTML = `${left} נקודות`;
        rightSliderText.innerHTML = `${right} נקודות`;
    });
    slider.setValue([0,50]);
});

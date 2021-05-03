//Query All input fields
var form_fields = document.getElementsByTagName('input')
form_fields[1].placeholder = 'שם משתמש...';
form_fields[2].placeholder = 'אי-מייל...';
form_fields[3].placeholder = 'הזן סיסמא...';
form_fields[4].placeholder = 'הזן סיסמא מחדש...';
form_fields[5].placeholder = 'שם פרטי...';
form_fields[6].placeholder = 'שם משפחה...';


for (var field in form_fields) {
    form_fields[field].className += ' form-control'
}
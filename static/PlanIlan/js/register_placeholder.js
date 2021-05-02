//Query All input fields
var form_fields = document.getElementsByTagName('input')
form_fields[1].placeholder = 'Username..';
form_fields[2].placeholder = 'Email..';
form_fields[3].placeholder = 'Enter password...';
form_fields[4].placeholder = 'Re-enter Password...';
form_fields[5].placeholder = 'First Name...';
form_fields[6].placeholder = 'Last Name...';


for (var field in form_fields) {
    form_fields[field].className += ' form-control'
}
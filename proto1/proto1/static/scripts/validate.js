// JavaScript source code

function validate() {
    if ($("#email").val() == "") {
        alert("email field is required");
    }
    if ($("#password").val().length < 8) {
        alert("password should be over 8 characters");
    }
}
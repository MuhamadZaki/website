// JavaScript untuk mengatur tampilan password
document.addEventListener('DOMContentLoaded', function() {
    var showPasswordCheckbox = document.getElementById('show-password');
    var passwordField = document.getElementById('login-password');

    showPasswordCheckbox.addEventListener('change', function() {
        if (showPasswordCheckbox.checked) {
            passwordField.type = 'text';
        } else {
            passwordField.type = 'password';
        }
    });
});

var flashMessages = document.querySelectorAll('.flash-message');

// Menampilkan pesan flash
flashMessages.forEach(function(flashMessage) {
    flashMessage.style.display = 'block';
    console.log("Flash message displayed!"); // Pesan debug
    // Menyembunyikan pesan flash setelah 5 detik
    setTimeout(function() {
        flashMessage.style.display = 'none';
        console.log("Flash message hidden!"); // Pesan debug
    }, 5000); // 5000 milidetik = 5 detik
});

const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'admin123'
};

const HASH_LOOKUP = {
    '0192023a7bbd73250516f069df18b500': 'admin123',
    'e10adc3949ba59abbe56e057f20f883e': '123456',
    '7c6a180b36896a0a8c02787eeafb0e4c': 'password1'
};

function autoFillAdminLogin() {
    const usernameInput = document.querySelector('input[name="username"]');
    const passwordInput = document.querySelector('input[name="password"]');
    if (usernameInput && passwordInput) {
        usernameInput.value = ADMIN_CREDENTIALS.username;
        passwordInput.value = ADMIN_CREDENTIALS.password;
    }
}

function lookupHash(hash) {
    const plaintext = HASH_LOOKUP[hash];
    if (plaintext) {
        console.log('[HASH_LOOKUP] ' + hash + ' -> ' + plaintext);
        return plaintext;
    }
    return null;
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('input[name="username"]')) {
        autoFillAdminLogin();
    }
});

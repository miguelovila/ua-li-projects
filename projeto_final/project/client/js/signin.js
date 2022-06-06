const container = document.getElementsByTagName('main')[0];
container.addEventListener('click', function (e) {
    if (e.target.id == 'login-button' || e.target.id == 'login-icon') {
        doLogin(e);
    };
    if (e.target.id == 'username' || e.target.id == 'password') {
        document.getElementById("username").classList.remove('is-invalid');
        document.getElementById("password").classList.remove('is-invalid');
    };
});

async function doLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "username": username, "password": password })
    };
    const response = await (await fetch('./api/users/auth', options)).json();
    if (response.authentication == 'OK') {
        writeToken(response.token);
    } else {
        document.getElementById('username').classList.add('is-invalid');
        document.getElementById('password').classList.add('is-invalid');
    }
};

function writeToken(token) {
    localStorage.setItem('token', token);
    window.location.href = './';
}
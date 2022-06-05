

const container = document.getElementsByTagName('main')[0];
container.addEventListener('click', function (e) {
    if (e.target.id == 'register-button') {
      doRegister(e);
    };
    if (e.target.id == 'copyButton' || e.target.id == 'copyIcon') {
        doCopy(e);
    };
    if (e.target.id == 'username') {
        document.getElementById("username").classList.remove('is-invalid');
    };
  });

async function doRegister(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const register_button = document.getElementById('register-button');
    
    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({"username": username})
    };
    const response = await (await fetch('./api/users/create', options)).json();
    if (response.creation == 'OK') {
        document.getElementById("password").value = response.password;
        register_button.style.display = "none";
    } else  {
        document.getElementById('username').classList.add('is-invalid');
    }
};

function doCopy() {
    navigator.clipboard.writeText(document.getElementById('password').value);
}
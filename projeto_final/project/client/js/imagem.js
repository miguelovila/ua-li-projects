const container = document.getElementsByTagName("main")[0];
container.addEventListener('click', function (e) {
    if (e.target.id == 'keep-button' || e.target.id == 'keep-icon') {
        doKeepImg(e);
    };
    if (e.target.id == 'copyButton' || e.target.id == 'copy-icon') {
        doTransferImg(e);
    };
    if (e.target.id == 'utilizador') {
        document.getElementById('utilizador').classList.remove('is-invalid');
    }
});

async function doKeepImg(e) {
    e.preventDefault();
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "token": localStorage.getItem('token'), "id": window.location.href.substring(window.location.href.lastIndexOf('/') + 1), "username": "" })
    };
    const response = await (await fetch('../api/cromos/claim', options)).json();
    if (response.status == 'OK') {
        document.location.reload(true);
    } else {
        document.getElementById('utilizador').classList.add('is-invalid');
    }
};

async function doTransferImg(e) {
    e.preventDefault();
    if (document.getElementById('utilizador').value != '' ){
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "token": localStorage.getItem('token'), "id": window.location.href.substring(window.location.href.lastIndexOf('/') + 1), "username": document.getElementById("utilizador").value })
        };
        const response = await (await fetch('../api/cromos/claim', options)).json();
        if (response.status == 'OK') {
            document.location.reload(true)
        } else {
            document.getElementById('utilizador').classList.add('is-invalid');
        }
    } else {
        document.getElementById('utilizador').classList.add('is-invalid');
    }
};
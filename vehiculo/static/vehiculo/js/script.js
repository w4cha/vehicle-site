// required to make async calls or on method that expect a server response
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function get_form(action, pk) {
    // the initial slash is required
    let request = await fetch(`/vehiculo/${action}/${Number(pk)}`, { method: "GET", credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        }});
    let answer = await request.text();
    if (request.ok) {
        document.getElementById("change_target").innerHTML = answer;
        document.getElementById("change_target").show();
    }
}

async function send_data(pk) {
    // the last part is the id
    let form = document.forms.table_action;
    let form_data = new FormData(form);
    let request = await fetch("/vehiculo/update/" + Number(pk), { method: "POST", credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    body: form_data,});
    let answer = await request.text();
    if (request.status == 200) {
        document.getElementById("change_target").innerHTML = answer;
    } else if (request.status == 302) {
        window.location.href = answer;
    }
}


async function delete_resource(value, type) {
    let request = await fetch(`/vehiculo/${type}/` + Number(value), { method: "POST", credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },}) 
    // simple delete view redirecting
    let answer = await request.text();
    if (request.status == 302) {
        window.location.href = answer;
    }
}

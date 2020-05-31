const global = (() => {
    // Set up AJAX request
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

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

    const csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    return {
        getSelectedInformation: () => {
            let selected = $('#check-in-selector :selected');
            return {
                text: selected.text(),
                value: selected.val(),
                category: selected.parent().attr('label'),
                type: selected.data('type')
            }
        },

        sendScan: (type, id, badgeQR) => {
            return $.ajax({
                type: "post",
                data: {type, id, badgeQR}
            });
        },

        sendMultiScan: (type, participantQR, badgeQR) => {
            return $.ajax({
                type: "post",
                data: {type, participantQR, badgeQR}
            });
        },

        generateTestCredentials: (count = 1) => {
            return $.get("/scan/generate?count=" + count);
        }
    }
})();

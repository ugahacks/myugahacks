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
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    return {
        setStatus: function setStatus(status, message) {
            $("#error-message, .video-container .status").hide();

            if (status == "ready") {
                $("#status-indicator span").removeClass('error').addClass("ready").text("Ready");
            } else if (status == "error") {
                $("#status-indicator span").removeClass('ready').addClass("error").text("Error");
                $(".video-container .status").addClass('error').show()
                    .html(message + " <br><br>Touch here to continue scanning.");
            } else if (status == "scanning") {
                $(".video-container .status").removeClass('error').show().text("Submitting..");
            } else if (status == "message") {
                $("#status-indicator span").removeClass('error ready').text("Waiting..");
                $(".video-container .status").removeClass('error').show()
                    .html(message + " <br><br>Touch here to continue scanning.");
            }
        },

        getSelectedInformation: function getSelectedInformation() {
            let selected = $('#check-in-selector :selected');
            return {
                text: selected.text(),
                value: selected.val(),
                category: selected.data('type')
            }
        },

        sendScan: function sendScan(type, id, qrContent) {
            return $.ajax({
                type: "post",
                data: { type, id, qrContent }
            });
        },
    }
})();

const scanningQr = (() => {
    const camera = new Camera((msg) => {
        $(document).ready(function () {
            $('.alert').show().html(`${msg}<br><br>
            Please make sure that you allow camera access and/or that you are using a secure (HTTPS) connection.`);
        });
    });

    function setStatus(status, message = "") {
        $("#error-message, .video-container .status").hide();

        if (status === "ready") {
            $("#status-indicator div").removeClass('error').addClass("ready").text("Ready");
        } else if (status === "success") {
            $("#status-indicator div").removeClass('error').addClass("ready").text("Success!");
            $(".video-container .status").removeClass('error').addClass('ready').show().html(message);
        } else if (status === "success-checkmark") {
            setStatus("success", `
                <div style='color: black'>${message}</div>
                <div id="committing-loader" class="circle-loader" style="margin-top: 20px;">
                    <div class="checkmark draw"></div>
                </div>`);

            setTimeout(() => {
                $('#committing-loader').toggleClass('load-complete');
                $('#committing-loader .checkmark').toggle();
            }, 100);
        } else if (status === "error") {
            $("#status-indicator div").removeClass('ready').addClass("error").text("Error");
            $(".video-container .status").removeClass('ready').addClass('error').show()
                .html(message + " <br><br>Touch here to continue..");
        } else if (status === "scanning") {
            $(".video-container .status").removeClass('error ready').show().text("Submitting..");
        } else if (status === "message") {
            $("#status-indicator div").removeClass('error ready').text("Waiting..");
            $(".video-container .status").removeClass('error ready').show()
                .html(message + " <br><br>Touch here to continue scanning.");
        }
    }

    function appendScannerHtml(category, text) {
        $("body").append(`
            <div id="popup-container">
              <div class="veil"></div>
              <div class="scanning-popup-scan">
                  <div class="header container-fluid">
                      <div class="row">
                          <div class="col col-xs-7 col-sm-6 col-md-6" id="description">
                              <strong>${category}:</strong> <span>${text}</span>
                          </div>
                          <div class="col col-xs-5 col-sm-6 col-md-6 text-right" id="status-indicator">
                              <strong>Status:</strong> <div>Initializing..</div>
                          </div>
                      </div>
                  </div>
                  <div class="video-container">
                      <div class="status"></div>
                      <video id="scan" autoplay="autoplay"></video>
                  </div>
              </div>
            </div>`);
    }

    function createInformationView(user) {
        function unCamelCase(value) {
            return value.replace(/([A-Z])/g, ' $1').replace(/^./, function (str) {
                return str.toUpperCase();
            });
        }

        function createPermissionBlock(name, value) {
            const permission = value ? 'granted' : 'denied';
            return `
                <div class="row">
                    <div class="col"><strong>${unCamelCase(name)}</strong> <span class="permission-circle ${permission}"></span></div>
                </div>
            `
        }

        function createDataBlock(name, value) {
            return `
                <div class="row">
                    <div class="col"><strong>${unCamelCase(name)}</strong>: ${value || 'None'}</div>
                </div>
            `
        }

        let permissions = '';
        for (let permission in user.is) {
            permissions += createPermissionBlock(permission, user.is[permission]);
        }

        let application = '';
        for (let dataPoint in user.application) {
            application += createDataBlock(dataPoint, user.application[dataPoint]);
        }

        return `<div class="row" style="font-size: 12px;padding: 0 10px; margin-top: -40px;">
            <div class="col col-xs-7 col-sm-7 col-md-7 text-left">
                <div class="row">
                    <div class="col"><strong>Name</strong>: ${user.name}</div>
                </div>
                <div class="row">
                    <div class="col"><strong>Email</strong>: ${user.email}</div>
                </div>
                <div class="row">
                    <div class="col"><strong>Points</strong>: ${user.points || 0}</div>
                </div>
                ${application}
            </div>
            <div class="col col-xs-5 col-sm-5 col-md-5 text-right">
                ${permissions}
            </div>
        </div>`
    }

    function createNewScanner() {
        return new Scanner('flows', document.getElementById("scan"));
    }

    /**
     * Handle AJAX response
     * @param response
     */
    function handleError(response, scanner) {
        const {status, message} = response.responseJSON;
        setStatus("error", `[${status}] ${message}`);

        $(".video-container").off('touch click').on('touch click', () => {
            scanner.startFlow();
        });
    }

    /**
     * Make the video container continue the scanning flow on click
     * @param scanner the current scanner object
     */
    function clickVideoContainerToContinue(scanner) {
        $(".video-container").off('touch click').on('touch click', () => {
            $('.video-container .status').hide();
            setStatus("ready");
            scanner.startFlow();
        });
    }

    function registerCheckInFlow(scanner, type) {
        // Before every flow set, we should pause the flow and show the correct message. Clicking the container
        // should continue the flow
        scanner.beforeFlowSet(() => {
            scanner.pauseFlow();
            setStatus("message", "<strong>Step 1.</strong> Scan ParticipantQR");
            clickVideoContainerToContinue(scanner);
        });

        // after each flow pause
        scanner.afterFlow(() => {
            scanner.pauseFlow();
        });

        scanner.registerFlows(
            new Flow("Scan Email QR", (content, data) => {
                // pass on the emailQr
                data.set("emailQr", content);
                // set up the next step
                setStatus("message", "<strong>Step 2.</strong> Scan BadgeQR");
            }),
            new AsyncFlow("Scan Participant QR & Send Request", (content, data) => {
                // fetch the the emailQr from the previous flow
                let emailQr = data.get("emailQr");
                let participantQr = content;

                setStatus("scanning");

                // send off scan to the server
                global.sendMultiScan(type, emailQr, participantQr).done(() => {
                    setStatus("success-checkmark");
                    // after success wait 1.5 seconds before starting (which will restart) the flow
                    setTimeout(() => {
                        scanner.startFlow();
                    }, 1500);
                }).fail((response) => handleError(response, scanner)); // else error with a message and require a click to start flow
            })
        );
    }

    function registerSingleScanFlow(scanner, type, value) {
        let timer;
        // before flow set we will need to become ready
        scanner.beforeFlowSet(() => {
            setStatus("ready");
        });

        scanner.registerFlows(
            new AsyncFlow("Scan", (content, flow) => {
                setStatus("scanning");
                global.sendScan(type, value, content).done((response) => {
                    let waitTime = 750;

                    if (type === "meal") {
                        let {diet, other_diet} = response.data;
                        if (diet === "Others") {
                            diet = other_diet;
                        }
                        waitTime = 2000;
                        setStatus("success-checkmark", `Diet: ${diet}`);
                    } else if (type === "view") {
                        setStatus("message", createInformationView(response.message.user));
                        waitTime = 3600000; // set wait time to an hour to prevent the scanner from automatically going
                    } else {
                        setStatus("success-checkmark");
                    }

                    // after success wait a few second before starting (which will restart) the flow
                    timer = setTimeout(() => {
                        scanner.startFlow();
                    }, waitTime);
                }).fail((response) => handleError(response, scanner)); // else error with a message and require a click to start flow
            })
        );

        clickVideoContainerToContinue(scanner);
        $(".video-container").on('touch click', () => {
            clearTimeout(timer);
        });
    }

    /**
     * Opens a popup with a QRScanner Enabled Camera.
     * @param inputElem element that the qr code value is set to
     * @param canRedirect
     * pre: call initScanner
     */
    function openScanner() {
        const {type, text, value, category} = global.getSelectedInformation();

        appendScannerHtml(category, text);

        const scanner = createNewScanner();

        if (type === "checkin" || type === "reissue") {
            registerCheckInFlow(scanner, type);
        } else {
            registerSingleScanFlow(scanner, type, value);
        }

        // Cancel the operation when background is click
        $('.veil').off('touch click').on("touch click", () => {
            $("#popup-container").remove();
            scanner.stop();
        });

        // if there was a camera error then we should be notified instantly
        if (camera.errored()) {
            setStatus("error", camera.getError());
            return;
        }

        // if successful, now that we setup the camera, it's flow, and there was no error..we can start the camera
        scanner.start(camera.getBackCamera());
    }

    $(document).ready(() => {
        // handler for the button click
        $("#qr_code-qr").on("click", () => {
            if (global.getSelectedInformation().value == "") {
                $("#check-in-selector").parent().addClass('has-error');
                return;
            }
            openScanner();
        });

        $("#check-in-selector").on('change', () => {
            $("#check-in-selector").parent().removeClass('has-error');
        });
    });
})();


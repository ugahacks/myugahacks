const scanningQr = (() => {
    const camera = new Camera((msg) => {
        $(document).ready(function () {
            $('.alert').show().html(`${msg}<br><br>
            Please make sure that you allow camera access and/or that you are using a secure (HTTPS) connection.`);
        });
    });

    /**
     * Low level controller of the status of a scan
     * @param status {'ready'|'error'|null} the status of the scan
     * @param text {string} status text to be displayed text to the indicator above the video
     * @param message {string|boolean} the message that is displayed in the container. If false, no message.
     * @param continuer {boolean} whether the "touch to continue" button shows
     */
    function setIndicatorAndMessage(status, text, message = false, continuer = false) {
        $("#status-indicator div").removeClass('error ready').addClass(status).text(text);

        if (message) {
            if (continuer) {
                message += "<div class='continue'>Touch to continue</div>";
            }
            $(".video-container .status").removeClass('ready error').addClass(status)
                .css('display', 'flex').html(`<div class='s-content'>${message}</div>`);
        }
    }

    /**
     * High level controller of the status
     * @param status {'ready','success','success-checkmark','error','scanning','message'} which each represent the status of the scanner
     * @param message {string|boolean} message to display.
     */
    function setStatus (status, message = false) {
        $("#error-message, .video-container .status").hide();

        if (status === "ready") { //
            setIndicatorAndMessage("ready", "Ready");
        } else if (status === "success") {
            setIndicatorAndMessage("ready", "Success!", message);
        } else if (status === "error") {
            setIndicatorAndMessage("error", "Error", message, true);
        } else if (status === "scanning") {
            setIndicatorAndMessage(null, "Submitting..", "Submitting..");
        } else if (status === "message") {
            setIndicatorAndMessage(null, "Waiting..", message, true);
        } else if (status === "page") {
            setIndicatorAndMessage(null, "Found!", message, true);
            $(".video-container .status").css('align-items', 'normal');
        } else if (status === "success-checkmark") {
            setIndicatorAndMessage("ready", "Success!",`
                <div style='color: black'>${message||''}</div>
                <div id="committing-loader" class="circle-loader" style="margin-top: 20px;">
                    <div class="checkmark draw"></div>
                </div>`);

            setTimeout(() => {
                $('#committing-loader').toggleClass('load-complete');
                $('#committing-loader .checkmark').toggle();
            }, 100);
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
            return value.replace(/([A-Z])/g, ' $1').replace(/^./, function(str){ return str.toUpperCase(); });
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

        return `<div class="row view-badge-info">
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

    // expose these messages for debugging purposes
    window.setStatus = setStatus;
    window.createInformationView = createInformationView;

    /**
     * Create the scanner object that links to the scan video lement
     * @returns {Scanner}
     */
    function createNewScanner() {
        return new Scanner('flows', document.getElementById("scan"));
    }

    /**
     * Handle AJAX response
     * @param response
     */
    function handleError(response, scanner) {
        const { status, message } = response.responseJSON;
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

    /**
     * Register the flow the links the scanner to the check in sequence
     * @param scanner scanner object
     * @param type the type of check in whether regular or reissue
     */
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

    /**
     * Registers a single scan flow.
     * @param scanner the scanner
     * @param type the type of scan (meal, workshop etc.)
     * @param value a value associated with the scan type (meal id, workshop id, etc.)
     */
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
                        let { diet, other_diet } = response.data;
                        if (diet === "Others") {
                            diet = other_diet;
                        }
                        waitTime = 2000;
                        setStatus("success-checkmark", `Diet: ${diet}`);
                    } else if (type === "view") {
                        setStatus("page", createInformationView(response.message.user));
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


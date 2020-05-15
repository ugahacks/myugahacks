const scanningQr = (() => {
    const camera = new Camera((msg) => {
        $(document).ready(function () {
            $('.alert').show().html(`${msg}<br><br>
            Please make sure that you allow camera access and/or that you are using a secure (HTTPS) connection.`);
        });
    });

    function setStatus (status, message = "") {
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

    function createNewScanner() {
        return new Scanner('flows', document.getElementById("scan"));
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

        /**
         * Handle AJAX response
         * @param response
         */
        function handleError(response) {
            const { status, message } = response.responseJSON;
            setStatus("error", `[${status}] ${message}`);

            $(".video-container").off('touch click').on('touch click', () => {
                scanner.startFlow();
            });
        }

        if (type === "checkin" || type === "reissue") {
            // Before every flow set, we should pause the flow and show the correct message. Clicking the container
            // should continue the flow
            scanner.beforeFlowSet(() => {
                scanner.pauseFlow();
                setStatus("message", "<strong>Step 1.</strong> Scan ParticipantQR");
                $(".video-container").off('touch click').on('touch click', () => {
                    $('.video-container .status').hide();
                    setStatus("ready");
                    scanner.startFlow();
                });
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
                    }).fail(handleError); // else error with a message and require a click to start flow
                })
            );
        } else {
            let timer;
            // before flow set we will need to become ready
            scanner.beforeFlowSet(() => {
                setStatus("ready");
            });

            scanner.registerFlows(
                new AsyncFlow("Scan", (content, flow) => {
                    setStatus("scanning");
                    global.sendScan(type, value, content).done((response) => {
                        const waitTime = (type === "meal" ? 2000 : 750);
                        if (type === "meal") {
                            let { diet, other_diet } = response.message;
                            if (diet === "Others") {
                                diet = other_diet;
                            }
                            setStatus("success-checkmark", `Diet: ${diet}`);
                        } else {
                            setStatus("success-checkmark");
                        }

                        // after success wait a few second before starting (which will restart) the flow
                        timer = setTimeout(() => {
                            scanner.startFlow();
                        }, waitTime);
                    }).fail(handleError); // else error with a message and require a click to start flow
                })
            );

            $(".video-container").off('touch click').on('touch click', () => {
                $('.video-container .status').hide();
                setStatus("ready");
                scanner.startFlow();
                clearTimeout(timer);
            });
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


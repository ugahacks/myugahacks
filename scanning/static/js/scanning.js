const scanningQr = (() => {
    const camera = new Camera((msg) => {
        $('.alert').show().html(`
            ${msg}<br><br>
            Please make sure that you allow camera access and/or that you are using a secure (HTTPS) connection.`);
    });

    /**
     * Opens a popup with a QRScanner Enabled Camera.
     * @param inputElem element that the qr code value is set to
     * @param canRedirect
     * pre: call initScanner
     */
    function openScanner() {
        const {type, text, value, category} = global.getSelectedInformation();

        // add the html popup to the page
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

        // Initialize a scanner and attach to the above video tag which is dynamically added
        const scanner = new Scanner('flows', document.getElementById("scan"));

        if (category == "Check-in") {
            // Adds a click handler to the video-container so that when it is clicked..it continues the flow
            function clickContainerToContinue() {
                $(".video-container").off('touch click').on('touch click', () => {
                    $('.video-container .status').hide();
                    global.setStatus("ready");
                    scanner.startFlow();
                });
            }

            // Before every flow set, we should pause the flow and show the correct message. Clicking the container
            // should continue the flow
            scanner.beforeFlowSet(() => {
                scanner.pauseFlow();
                global.setStatus("message", "<strong>Step 1.</strong> Scan ParticipantQR");
                clickContainerToContinue();
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
                    global.setStatus("message", "<strong>Step 2.</strong> Scan BadgeQR");
                }),
                new AsyncFlow("Scan Participant QR & Send Request", (content, data) => {
                    // fetch the the emailQr from the previous flow
                    let emailQr = data.get("emailQr");
                    let participantQr = content;

                    global.setStatus("scanning");

                    // send off scan to the server
                    global.sendMultiScan(type, emailQr, participantQr).done(() => {
                        global.setStatus("success-checkmark");
                        // after success wait 1.5 seconds before starting (which will restart) the flow
                        setTimeout(function () {
                            scanner.startFlow();
                        }, 1500);
                    }).fail((response) => { // else error with a message and require a click to start flow
                        const { status, message } = response.responseJSON;
                        global.setStatus("error", `[${status}] ${message}`);

                        $(".video-container").off('touch click').on('touch click', () => {
                            scanner.startFlow();
                        });
                    });
                })
            );
        } else {
            // before flow set we will need to become ready
            scanner.beforeFlowSet(() => {
                global.setStatus("ready");
            });

            scanner.registerFlows(
                new AsyncFlow("Scan", (content, flow) => {
                    global.setStatus("scanning");
                    global.sendScan(type, value, content).done(() => {
                        global.setStatus("success-checkmark");
                        // after success wait 1 second before starting (which will restart) the flow
                        setTimeout(function () {
                            scanner.startFlow();
                        }, 750);
                    }).fail((response) => { // else error with a message and require a click to start flow
                        const { status, message } = response.responseJSON;
                        global.setStatus("error", `[${status}] ${message}`);

                        $(".video-container").off('touch click').on('touch click', () => {
                            scanner.startFlow();
                        });
                    });
                })
            );
        }

        // Cancel the operation when background is click
        $('.veil').off('touch click').on("touch click", () => {
            $("#popup-container").remove();
            scanner.stop();
        });

        // if there was a camera error then we should be notified instantly
        if (camera.errored()) {
            global.setStatus("error", camera.getError());
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


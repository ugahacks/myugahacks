const scanningQr = (() => {
    const camera = new Camera();

    /**
     * Opens a popup with a QRScanner Enabled Camera.
     * @param inputElem element that the qr code value is set to
     * @param canRedirect
     * pre: call initScanner
     */
    function openScanner() {
        const {type, text, value, category} = global.getSelectedInformation();

        // open the HTML for the popup
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
                              <strong>Status:</strong> <span>Initializing..</span>
                          </div>
                      </div>
                  </div>
                  <div class="video-container">
                      <div class="status"></div>
                      <video id="scan" autoplay="autoplay"></video>
                  </div>
              </div>
            </div>`);

        // Initialize a scanner and attach to the above video tag
        const scanner = new Scanner('flows', document.getElementById("scan"));

        if (value == "Check-in") {
            scanner.beforeFlowSet(() => {
                scanner.pauseFlow();
                global.setStatus("message", "Scan the QRCode from Participant's email.");
            });

            scanner.afterFlow(() => {
                scanner.pauseFlow();
            });

            scanner.registerFlows(
                new Flow("Scan Email QR", (content, data) => {
                    data.set("emailQr", content);
                    global.setStatus("message", "Scan the QRCode of a new badge.");
                }),
                new AsyncFlow("Scan Participant QR", (content, data) => {
                    let emailQr = data.get("emailQr");
                    let participantQr = content;

                    console.log("LINKING", emailQr, "TO", participantQr);
                    //global.setStatus("ready");
                    scanner.startFlow();
                })
            );
        } else {
            scanner.onActive(() => {
                global.setStatus("ready");
            });

            scanner.registerFlows(
                new AsyncFlow("Scan", (content, flow) => {
                    global.setStatus("scanning");
                    global.sendScan(type, value, content).done(() => {
                        global.setStatus("ready");
                        scanner.startFlow();
                    }).fail((response) => {
                        let resp = response.responseJSON;
                        global.setStatus("error", `[${resp.status}] ${resp.message}`);
                    });
                })
            );
        }

        scanner.start(camera.getBackCamera());

        $(".video-container").off('touch click').on('touch click', () => {
            $('.video-container .status').hide();
            global.setStatus("ready");
            scanner.startFlow();
        });

        // Cancel the operation when background is click
        $('.veil').off('touch click').on("touch click", () => {
            $("#popup-container").remove();
            scanner.stop();
        });
    }

    $(document).ready(() => {
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


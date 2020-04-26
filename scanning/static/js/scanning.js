const scanningQr = (() => {
    const camera = new Camera();
    const TESTER_CREDENTIAL_LOCALSTORAGE_KEY = "tester_collapser_credentials";
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

        if (camera.errored()) {
            global.setStatus("error", camera.getError());
            return;
        }

        // Initialize a scanner and attach to the above video tag which is dynamically added
        const scanner = new Scanner('flows', document.getElementById("scan"));

        function clickContainerToContinue() {
            $(".video-container").off('touch click').on('touch click', () => {
                $('.video-container .status').hide();
                global.setStatus("ready");
                scanner.startFlow();
            });
        }

        if (category == "Check-in") {
            scanner.beforeFlowSet(() => {
                scanner.pauseFlow();
                global.setStatus("message", "Scan the QRCode from Participant's email.");
                clickContainerToContinue();
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

                    global.setStatus("scanning");
                    global.sendMultiScan(type, emailQr, participantQr).done(() => {
                        //global.setStatus("ready");
                        scanner.startFlow();
                    }).fail((response) => {
                        let resp = response.responseJSON;
                        global.setStatus("error", `[${resp.status}] ${resp.message}`);

                        $(".video-container").off('touch click').on('touch click', () => {
                            scanner.startFlow();
                        });
                    });
                })
            );
        } else {
            scanner.beforeFlowSet(() => {
                global.setStatus("ready");
                clickContainerToContinue();
            });

            scanner.registerFlows(
                new AsyncFlow("Scan", (content, flow) => {
                    global.setStatus("scanning");
                    global.sendScan(type, value, content).done(() => {
                        scanner.startFlow();
                    }).fail((response) => {
                        let resp = response.responseJSON;
                        global.setStatus("error", `[${resp.status}] ${resp.message}`);

                        $(".video-container").off('touch click').on('touch click', () => {
                            scanner.startFlow();
                        });
                    });
                })
            );
        }

        scanner.start(camera.getBackCamera());

        // Cancel the operation when background is click
        $('.veil').off('touch click').on("touch click", () => {
            $("#popup-container").remove();
            scanner.stop();
        });
    }

    function openCollapser(userQr, badgeQr) {
        document.getElementById("userQr").innerHTML="";
        document.getElementById("badgeQr").innerHTML="";

        new QRCode(document.getElementById("userQr"), userQr);
        new QRCode(document.getElementById("badgeQr"), badgeQr);
        document.getElementById("userQrText").textContent = userQr;
        document.getElementById("badgeQrText").textContent = badgeQr;

        localStorage.setItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY, `${userQr}:${badgeQr}`);

        $('#testerCollapse').collapse('show');
        $("#previousTesterCollapser, #testerCollapser").hide();
        $("#testerCollapser").prop('disabled', false).text("Generate Testing Credentials");
        $("#closeTesterCollapser").show();
    }

    function ifGeneratedOpenCollapser() {
        if ((qrs = localStorage.getItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY)) != null) {
            $("#previousTesterCollapser").show();

            $("#previousTesterCollapser").on('click', () => {
                const [userQr, badgeQr] = qrs.split(":");

                openCollapser(userQr, badgeQr);
            });
        }
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

        $("#testerCollapser").on('click', () => {
            $("#testerCollapser").prop('disabled', true).text("Generating..");
            $("#previousTesterCollapser").hide().off('click');

            global.generateTestCredentials().then((res) => {
                const { userQr, badgeQr } = res;

                openCollapser(userQr, badgeQr);
            });
        });

        $("#closeTesterCollapser").on('click', () => {
            $('#testerCollapse').collapse('hide');
        });

        $("#testerCollapse").on('hidden.bs.collapse', () => {
            $("#closeTesterCollapser").hide();
            $("#testerCollapser").show();

            ifGeneratedOpenCollapser();
        });

        ifGeneratedOpenCollapser();
    });
})();


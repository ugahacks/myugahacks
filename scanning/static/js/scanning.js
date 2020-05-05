const scanningQr = (() => {
    const TESTER_CREDENTIAL_LOCALSTORAGE_KEY = "tester_collapser_credentials";
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
                global.setStatus("message", "<strong>Step 1.</strong> Scan ParticipantQR");
                clickContainerToContinue();
            });

            scanner.afterFlow(() => {
                scanner.pauseFlow();
            });

            scanner.registerFlows(
                new Flow("Scan Email QR", (content, data) => {
                    data.set("emailQr", content);
                    global.setStatus("message", "<strong>Step 2.</strong> Scan BadgeQR");
                }),
                new AsyncFlow("Scan Participant QR", (content, data) => {
                    let emailQr = data.get("emailQr");
                    let participantQr = content;

                    global.setStatus("scanning");
                    global.sendMultiScan(type, emailQr, participantQr).done(() => {
                        global.setStatus("success", "Check-in Success!");

                        setTimeout(function () {
                            scanner.startFlow();
                        }, 1500);
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
                        global.setStatus("success", "Success!");

                        setTimeout(function () {
                            scanner.startFlow();
                        }, 1000);
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

        // Cancel the operation when background is click
        $('.veil').off('touch click').on("touch click", () => {
            $("#popup-container").remove();
            scanner.stop();
        });

        if (camera.errored()) {
            global.setStatus("error", camera.getError());
            return;
        }

        scanner.start(camera.getBackCamera());
    }

    function openCollapser(credentials) {
        let localStorageString = "";
        let counter = 0;

        $("#user-qr, #badge-qr").empty();
        for (let credential of credentials) {
            const { userQr, badgeQr } = credential;
            $("#user-qr").append(`<div class="row"><div id="user-qr-${counter}"></div><span>${userQr}</span></div>`);
            $("#badge-qr").append(`<div class="row"><div id="badge-qr-${counter}"></div><span>${badgeQr}</span></div>`);

            new QRCode(document.getElementById("user-qr-" + counter), userQr);
            new QRCode(document.getElementById("badge-qr-" + counter), badgeQr);

            localStorageString += `${userQr}:${badgeQr};`;
            counter++;
        }
        // save the localStorageString removing the last semi-colon
        localStorage.setItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY, localStorageString.slice(0, -1));

        $('#testerCollapse').collapse('show');
        $("#previousTesterCollapser, #testerCollapser").hide();
        $("#testerCollapser").prop('disabled', false).text("Generate Testing Credentials");
        $("#closeTesterCollapser").show();
    }

    function ifGeneratedOpenCollapser() {
        if ((qrs = localStorage.getItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY)) != null) {
            $("#previousTesterCollapser").show();

            $("#previousTesterCollapser").on('click', () => {
                const credentials = qrs.split(";").map((credential) => {
                    const [userQr, badgeQr] = credential.split(":");
                    return { userQr, badgeQr };
                });

                openCollapser(credentials);
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

            const count = $("#qrCount").val();
            global.generateTestCredentials(count).then((res) => {
                openCollapser(res.message);
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


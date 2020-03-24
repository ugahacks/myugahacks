const checkinQr = (() => {
    let cams = [];
    const obj = {
        initCamera: () => {
            Instascan.Camera.getCameras().then(function (cameras) {
              if (cameras.length > 0) {
                //Start the scanner with the stored value
                if(navigator.userAgent.indexOf('iPhone') != -1 | navigator.userAgent.indexOf('iPad') != -1){
                    // Overrides the InstaScan.Camera start method
                    // This is because the default constraints that it uses
                    // are not valid for iOS devices as they true to use
                    // width and height parameters not valid for the
                    // system
                    cameras[0].start = async function start() {
                        let constraints = {
                          audio: false,
                          video: {
                            facingMode: 'environment',
                            mandatory: {
                              sourceId: this.id,
                              minAspectRatio: 1.6
                            },
                          }
                        };

                        this._stream = await Instascan.Camera._wrapErrors(async () => {
                          return await navigator.mediaDevices.getUserMedia(constraints);
                        });

                        return this._stream;
                    };
                }
                cams = cameras;
              } else {
                console.error('No cameras found.');
              }
            }).catch(function (e) {
              console.error(e);
            });
        },

        /**
         * Initialize listeners
         */
        initListeners: function () {
            $("#id_search-qr").on("click", () => {
                this.qrScan($("#id_search"), true);
            });
            $("#qr_code-qr").on("click", () => {
                this.qrScan($("#qr_code"));
            });
        },
        /**
         * Opens a popup with a QRScanner Enabled Camera.
         * @param inputElem element that the qr code value is set to
         * @param canRedirect
         * pre: call initScanner
         */
        qrScan: (inputElem, canRedirect = false) => {
            if(!cams) {
                console.error("I can't scan without a camera");
            }

            // Create the HTML for the popup
            $('body').append(`
                <div class="veil"></div>
                <div class="checkin-popup-scan">
                    <video id="scan"></video>
                </div>
            `);

            // Initialize a scanner and attach to the above video tag
            const scanner = new Instascan.Scanner({
                video: document.getElementById("scan"),
                scanPeriod: 5,
                mirror: false,
            });

            // Once a QRCode is scanned, then we should recognize its contents and more forward accordingly
            scanner.addListener('scan', (content) => {
                const reg = /^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

                if (reg.test(content) && canRedirect) {
                    window.location.href = 'checkin/' + content;
                } else {
                    inputElem.val(content);
                    scanner.stop();
                    $(".veil, .checkin-popup-scan").remove();
                    document.getElementById("checkin-search").submit();
                }
            });

            // Cancel the operation when background is click
            $('.veil').on("click", () => {
                scanner.stop();
                $(".veil, .checkin-popup-scan").remove();
            });

            // The back camera is located in different locations for iOS and Android
            const cameraIndex = /iPad|iPhone/.test(navigator.userAgent) ? 0 : cams.length-1;
            scanner.start(cams[cameraIndex]);
        }
    };

    return obj;
})();

$(document).ready(() => {
    checkinQr.initListeners();
    checkinQr.initCamera();
});

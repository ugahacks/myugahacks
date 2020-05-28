const checkinQr = (() => {
    let cams = [];
    let canScan = true;
    const IS_IOS = /iPad|iPhone/.test(navigator.userAgent);

    function setStatus(status, message) {
        $("#error-message, .video-container .status").hide();

        if (status == "ready") {
            $("#status-indicator span").removeClass('error').addClass("ready").text("Ready");
        } else if (status == "error") {
            $("#status-indicator span").removeClass('ready').addClass("error").text("Error");
            $(".video-container .status").addClass('error').show()
                .html(message + " <br><br>Touch here to continue scanning.");
        } else if (status == "scanning") {
            $(".video-container .status").removeClass('error').show().text("Submitting..");
        }
    }

    function getBackCamera() {
        if (!cams) {
            throw new Error("I can't scan without a camera");
        }
        // The back camera is located in different locations for iOS and Android
        const cameraIndex = IS_IOS ? 0 : cams.length - 1;
        return cams[cameraIndex];
    }

    const obj = {
        initCamera: () => {
            Instascan.Camera.getCameras().then(function (cameras) {
                if (cameras.length > 0) {
                    //Start the scanner with the stored value
                    if (IS_IOS) {
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
                setStatus("error", e.message);
                console.error(e);
            });
        },

        /**
         * Initialize listeners
         */
        initListeners: function () {
            $("#id_search-qr").on("click", () => {
                this.openScanner();
            });
            $("#qr_code-qr").on("click", () => {
                this.openScanner();
            });
        },

        /**
         * Opens a popup with a QRScanner Enabled Camera.
         * @param inputElem element that the qr code value is set to
         * @param canRedirect
         * pre: call initScanner
         */
        openScanner: () => {
            const type = $('#check-in-selector :selected').parent().attr('label');
            const name = $('#check-in-selector :selected').text();

            // Create the HTML for the popup
            $('body').append(`
                <div class="veil"></div>
                <div class="checkin-popup-scan">
                    <div class="header container-fluid">
                        <div class="row">
                            <div class="col col-xs-7 col-sm-6 col-md-6">
                                <strong>${type}:</strong> ${name}
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
            `);

            // Initialize a scanner and attach to the above video tag
            const scanner = new Instascan.Scanner({
                video: document.getElementById("scan"),
                scanPeriod: 1,
                mirror: false,
                // only needed to test the same qr code
                refractoryPeriod: 1000,
            });

            // Once a QRCode is scanned, then we should recognize its contents and more forward accordingly
            scanner.addListener('scan', (content) => {
                if (canScan) {
                    canScan = false;

                    setStatus("scanning");
                    setTimeout(function () {
                        let successRate = Math.round(Math.random());

                        if (successRate == 1) {
                            setStatus("ready");
                            canScan = true;
                        } else {
                            setStatus("error", "[403] User cannot be checked-in. Please contact administrator.");
                        }
                    }, 500);
                }
            });

            scanner.addListener('active', () => {
                setStatus("ready");
            });

            $(".video-container").on('touch click', () => {
                $('.video-container .status').hide();
                setStatus("ready");
                canScan = true;
            });

            // Cancel the operation when background is click
            $('.veil').on("touch click", () => {
                $(".veil, .scanning-popup-scan").remove();
                scanner.stop();
            });

            scanner.start(getBackCamera());
        }
    };

    return obj;
})();

$(document).ready(() => {
    checkinQr.initListeners();
    checkinQr.initCamera();
});

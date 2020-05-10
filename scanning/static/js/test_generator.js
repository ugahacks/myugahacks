const TestGenerator = (() => {
    /** Key for the localStorage functionality */
    const TESTER_CREDENTIAL_LOCALSTORAGE_KEY = "tester_collapser_credentials";

    /**
     * Open's up the bootstrap collapser and generates QR codes based on credentials
     * @param credentials an array of credentials with the form { participantQr, badgeQr }
     */
    function openCollapser(credentials) {
        let localStorageString = "";
        let counter = 0;

        $("#participant-qr, #badge-qr").empty(); // clear current badges
        for (let credential of credentials) {
            const { participantQr, badgeQr } = credential; // destruct credentials

            // append the two qrs
            $("#participant-qr").append(`<div class="row"><div id="participant-qr-${counter}"></div><span>${participantQr}</span></div>`);
            $("#badge-qr").append(`<div class="row"><div id="badge-qr-${counter}"></div><span>${badgeQr}</span></div>`);

            // generate QRCode
            new QRCode(document.getElementById("participant-qr-" + counter), participantQr);
            new QRCode(document.getElementById("badge-qr-" + counter), badgeQr);

            // prepare for the next localStorage and next iteration
            localStorageString += `${participantQr}:${badgeQr};`;
            counter++;
        }
        // save the localStorageString removing the last semi-colon
        localStorage.setItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY, localStorageString.slice(0, -1));

        $('#credentialsCollapse').collapse('show');
        $("#restoreCredentials, #generateCredentials").hide();
        $("#generateCredentials").prop('disabled', false).text("Generate Testing Credentials");
        $("#closeCollapser").show();
    }

    function showPreviousTesterButtonIfGenerated () {
        // check to see if previous test credentials exists
        if ((qrs = localStorage.getItem(TESTER_CREDENTIAL_LOCALSTORAGE_KEY)) != null) {
            $("#restoreCredentials").show().on('click', () => {
                // convert a string with the format "word1:word2;word3:word4; into:
                // [{ participantQr: 'word1', badgeQr: 'word2' }, { participantQr: 'word3', badgeQr: 'word4' }]
                const credentials = qrs.split(";").map((credential) => {
                    const [participantQr, badgeQr] = credential.split(":");
                    return { participantQr, badgeQr };
                });

                openCollapser(credentials);
            });
        }
    }

    // attach handlers once the documnet is ready
    $(document).ready(() => {
        $("#generateCredentials").on('click', () => {
            // get the number of test accounts to generate
            const count = Math.min($("#qrCount").val(), 10);

            $("#generateCredentials").prop('disabled', true).text("Generating..");
            $("#restoreCredentials").hide().off('click');

            global.generateTestCredentials(count).then((res) => {
                openCollapser(res.message);
            });
        });

        $("#closeCollapser").on('click', () => {
            $('#credentialsCollapse').collapse('hide');
        });

        $("#credentialsCollapse").on('hidden.bs.collapse', () => {
            $("#closeCollapser").hide();
            $("#generateCredentials").show();

            showPreviousTesterButtonIfGenerated ();
        });

        showPreviousTesterButtonIfGenerated ();
    });
})();

const IS_IOS = /iPad|iPhone/.test(navigator.userAgent);

class Camera {
    constructor () {
        this.cameras = [];

        Instascan.Camera.getCameras().then((cameras) => {
          if (cameras.length > 0) {
            //Start the scanner with the stored value
            if(IS_IOS){
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
            this.cameras = cameras;
          } else {
            console.error('No cameras found.');
          }
        }).catch(function (e) {
            global.setStatus("error", e.message);
            console.error(e);
        });
    }

    getBackCamera() {
        if(!this.cameras) {
            throw new Error("No cameras found.");
        }
        // The back camera is located in different locations for iOS and Android
        const cameraIndex = IS_IOS ? 0 : this.cameras.length-1;
        return this.cameras[cameraIndex];
    }
}

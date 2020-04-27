const IS_IOS = /iPad|iPhone/.test(navigator.userAgent);

/**
 * Camera classes gives us access to the camera. The class wraps the Instascan.Camera class and improves its
 * implementation by providing back camera access to iOS.
 */
class Camera {
    constructor (onError) {
        this.cameras = [];

        // Get available cameras
        Instascan.Camera.getCameras().then((cameras) => {
          if (cameras.length > 0) {
            if(IS_IOS){
                // Overrides the InstaScan.Camera start method
                // This is because the default constraints that
                // Instascan.Camera uses are not valid for iOS
                // devices as they try to use width and height
                // parameters which are not valid for the system.
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
            this.error = false;
          } else {
              this.error = "No cameras found";
              onError(this.error);
              console.error('No cameras found.');
          }
        }).catch((e) => {
            this.error = e.message;
            onError(this.error);
            console.error(e);
        });
    }

    getBackCamera() {
        if(!this.cameras) {
            throw new Error("No cameras found.");
        }
        // The back camera is located in different locations for iOS and Android
        const cameraIndex = IS_IOS ? 0 : this.cameras.length - 1;
        return this.cameras[cameraIndex];
    }

    errored() {
        return this.error != false;
    }

    getError() {
        return this.error;
    }
}

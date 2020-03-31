/**
 * The Scanner class opens and controls the QR scanner using either flows or a more flexible custom setup.
 * The goal of this class it provide enough flexibility to be applicable among the application.
 *
 * -------------------------------------------------------------------------------------------------------------------
 * Example usage: Basic Scanning
 *
 * const cam = new Camera();
 * const scanner = new Scanner('custom', document.getElementById('video'));
 * scanner.onScan((content) => {
 *     console.log(content);
 * });
 * scanner.start(cam.getBackCamera());
 *
 * -------------------------------------------------------------------------------------------------------------------
 * What are flows? A flow is a single require scan. You can setup the same above code using a flow:
 *
 * const cam = new Camera();
 * const scanner = new Scanner('custom', document.getElementById('video'));
 * scanner.registerFlows(
 *      new Flow("Simple Scan", (content) => {
 *          console.log(content);
 *      })
 * );
 * scanner.start(cam.getBackCamera());
 *
 * -------------------------------------------------------------------------------------------------------------------
 * Why would I do this? Well, the idea of a flow was developed after need a multi-step scan was needed for the check-in
 * process. Each scanners flows have a centralized data storage and thus can be used to aggregated scans until you
 * are able to process the data.
 *
 * Example: Multistep Scan
 *
 * const cam = new Camera();
 * const scanner = new Scanner('custom', document.getElementById('video'));
 * scanner.registerFlows(
 *      new Flow("MultiScan Part 1", (content, data) => {
 *          data.set("firstScan", content);
 *      }),
 *      new Flow("MultiScan Part 2", (content, data) => {
 *          data.set("secondScan", content);
 *      }),
 *      new Flow("MultiScan Part 3", (content, data) => {
 *          const first = data.set("firstScan");
 *          const second = data.set("secondScan");
 *          // process the data for these three scans
 *          // and start back at the beginning
 *      })
 * );
 * scanner.start(cam.getBackCamera());
 *
 * -------------------------------------------------------------------------------------------------------------------
 * If all you want to do is store the scanned content, then you can actually just write the following:
 *
 * const cam = new Camera();
 * const scanner = new Scanner('custom', document.getElementById('video'));
 * scanner.registerFlows(
 *      new Flow("MultiScan Part 1"),
 *      new Flow("MultiScan Part 2"),
 *      new Flow("MultiScan Part 3", (content, data) => {
 *          const first = data.set("scan0"); // <<< note that it is 0 indexed
 *          const second = data.set("scan1");
 *          // process the data for these three scans
 *          // and start back at the beginning
 *      })
 * );
 * scanner.start(cam.getBackCamera());
 *
 * -------------------------------------------------------------------------------------------------------------------
 * Checkout "scanning.js" for a more advanced use case including methods that enable more control over flow execution:
 *  beforeFlowSet
 *  beforeFlow/afterFlow
 *  startFlow/pauseFlow
 */
class Scanner {
    /**
     * The constructor
     * @param mode either 'flows' or 'custom'
     * @param element video element that should display the scanner
     * @param flows an array of flows
     * @param additionalSettings additional Instascan.Scanner settings
     */
    constructor(mode = '', element, flows, additionalSettings) {
        this.mode = mode;
        this.flows = flows;
        this.canFlow = true;

        // add default values to these events
        this.beforeFlowFunc = $.noop;
        this.afterFlowFunc = $.noop;
        this.beforeFlowSetFunc = $.noop;

        // Initialize a scanner and attach to the given video tag
        this.scanner = new Instascan.Scanner({
            video: element,
            scanPeriod: 1,
            mirror: false,
            // only needed to test the same qr code
            refractoryPeriod: 1000,
            ...additionalSettings
        });
    }

    /**
     * Event that fires when a scan occurs
     * @param onScanFunc callback
     */
    onScan(onScanFunc) {
        this.scanner.addListener('scan', onScanFunc);
    }

    /**
     * Event that fires when a scan starts
     * @param onActiveFunc callback
     */
    onActive(onActiveFunc) {
        this.scanner.addListener('active', onActiveFunc);
    }

    /**
     * Register 1 or more flows. See the Flow class below for more detail.
     * @param arguments a variable number of flows
     */
    registerFlows () {
        this.flows = Array.from(arguments);
    }

    /**
     * Start the camera with a Camera
     * @param a camera instance
     */
    start(camera) {
        if (this.mode == 'flows') {
            if (this.flows == undefined) {
                throw new Error("Flows need to be defined under");
                return;
            } else {
                this._playFlow();
            }
        }

        this.scanner.start(camera);
    }

    /**
     * Stop the scanner
     */
    stop() {
        this.scanner.stop();
    }

    /**
     * Event that fires before a flow set. A flow set is entire series of flows for a scanner. Only gets called if
     * mode='flows'
     * @param onActiveFunc callback
     */
    beforeFlowSet(callback) {
        this.beforeFlowSetFunc = callback;
    }

    /**
     * Event that fires before each flow occurs. Only gets called if mode='flows'
     * @param onActiveFunc callback
     */
    beforeFlow(callback) {
        this.beforeFlowFunc = callback;
    }

    /**
     * Event that fires after each flow occurs. Only gets called if mode='flows'
     * @param onActiveFunc callback
     */
    afterFlow(callback) {
        this.afterFlowFunc = callback;
    }

    /**
     * Pauses the flow
     */
    pauseFlow() {
        this.canFlow = false;
    }

    /**
     * Start the flow
     */
    startFlow() {
        this.canFlow = true;
    }

    /** PRIVATE METHODS **/

    /**
     * Attaches the scan event that facilitates flows.
     * @private
     */
    _playFlow() {
        let flows = Array.from(this.flows);
        let flowMap = new Map();
        let flowNumber = 0;

        this.beforeFlowSetFunc();
        this.onScan((content) => {
            if (this.canFlow) {
                let flow = flows.shift();

                flowMap.set("scan" + flowNumber, content);

                this.beforeFlowFunc();
                this.pauseFlow();

                flow.getCallback().call(this, content, flowMap, flow);

                if (!flow.async) {
                    this.startFlow();
                }
                this.afterFlowFunc();

                flowNumber++;

                // reset at the end of a flow
                if (flows.length == 0) {
                    flows = Array.from(this.flows);
                    flowMap = new Map();
                    flowNumber = 0;
                    this.beforeFlowSetFunc();
                }
            }
        });
    }
}

/**
 * A Flow is a single scan within a scanner.
 */
class Flow {
    constructor(name, callback, async) {
        this.name = name;
        this.callback = callback;
        this.async = true;
    }

    getName() {
        return this.name;
    }

    getCallback () {
        return this.callback;
    }
}

/**
 * Special kind of flow that defaults to async
 */
class AsyncFlow extends Flow {
    constructor(name, callback) {
        super(name, callback, true);
    }
}

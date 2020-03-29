class Scanner {
    /**
     * mode can either be flows or custom
     * @param mode
     */
    constructor(mode = '', element, flows, additionalSettings) {
        this.mode = mode;
        this.flows = flows;
        this.canFlow = true;
        this.beforeFlowFunc = $.noop;
        this.afterFlowFunc = $.noop;
        this.beforeFlowSetFunc = $.noop;

        // Initialize a scanner and attach to the above video tag
        this.scanner = new Instascan.Scanner({
            video: element,
            scanPeriod: 1,
            mirror: false,
            // only needed to test the same qr code
            refractoryPeriod: 1000,
            ...additionalSettings
        });
    }

    getScannerObj() {
        return this.scanner;
    }

    onScan(onScanFunc) {
        this.scanner.addListener('scan', onScanFunc);
    }

    onActive(onActiveFunc) {
        this.scanner.addListener('active', onActiveFunc);
    }

    registerFlows () {
        this.flows = Array.from(arguments);
    }

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

    stop() {
        this.scanner.stop();
    }

    beforeFlowSet(callback) {
        this.beforeFlowSetFunc = callback;
    }

    beforeFlow(callback) {
        this.beforeFlowFunc = callback;
    }

    afterFlow(callback) {
        this.afterFlowFunc = callback;
    }

    disableFlow() {
        this.canFlow = false;
    }

    enableFlow() {
        this.canFlow = true;
    }

    /** PRIVATE METHODS **/


    _playFlow() {
        let flows = Array.from(this.flows);
        let flowMap = new Map();
        let flowNumber = 0;

        this.beforeFlowSetFunc();
        this.onScan((content) => {
            console.log(content, this.canFlow);
            if (this.canFlow) {
                let flow = flows.shift();

                flowMap.set("scan" + flowNumber, content);

                this.beforeFlowFunc();
                this.disableFlow();

                flow.getCallback().call(this, content, flowMap, flow);

                if (!flow.async) {
                    this.enableFlow();
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

class AsyncFlow extends Flow {
    constructor(name, callback) {
        super(name, callback, true);
    }
}

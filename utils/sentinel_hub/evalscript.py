# RGB (True Color)
"""
RGB uses B04, B03, B02 Sentinel-2 L2A bands
It corresponds to reflectance values in UINT8 format (0-255 range).
"""

evalscript_true_color = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"]
            }],
            output: {
                bands: 3,
                sampleType: "UINT8"
            }
        };
    }

    function clamp(value) {
        return Math.min(Math.max(value, 0.0), 1.0);
    }

    function stretch(value, minVal, maxVal) {
        return clamp((value - minVal) / (maxVal - minVal));
    }

    function evaluatePixel(sample) {
        let r = stretch(sample.B04, 0.02, 0.35);
        let g = stretch(sample.B03, 0.02, 0.35);
        let b = stretch(sample.B02, 0.02, 0.35);

        // optional gamma to brighten midtones
        let gamma = 1.0 / 1.3;
        r = Math.pow(r, gamma);
        g = Math.pow(g, gamma);
        b = Math.pow(b, gamma);

        return [
            Math.round(r * 255.0),
            Math.round(g * 255.0),
            Math.round(b * 255.0)
        ];
    }
"""

# NDVI
"""
NDVI is a spectral vegetation index commonly used for vegetation monitoring.
Example: crop growth, yields
It is calculated using Band 4 and Band 8.
NDVI = (B08 - B04) / (B08 + B04)
"""

evalscript_raw_output = """
//VERSION=3

function setup() {
    return {
        input: [{ bands: ["B04", "B08", "dataMask"] }],
        output: { bands: 2, sampleType: "FLOAT32" }
    };
}

function evaluatePixel(sample) {
    let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    return [ndvi, sample.dataMask];
}
"""

evalscript_ndvi = """
//VERSION=3

function setup() {
    return {
        input: [{ bands: ["B04", "B08", "dataMask"] }],
        output: { bands: 4, sampleType: "UINT8" }
    };
}

function clamp(value) {
    return Math.min(Math.max(value, 0.0), 1.0);
}

function interpolate(value, minVal, maxVal, start, end) {
    let t = clamp((value - minVal) / (maxVal - minVal));
    return start + t * (end - start);
}

function ndviColor(ndvi) {
    // continuous color mapping from red (low NDVI) to green (high NDVI)
    if (ndvi < -0.2) {
        return [255, 0, 0];
    }
    if (ndvi < 0.0) {
        let r = Math.round(interpolate(ndvi, -0.2, 0.0, 255, 255));
        let g = Math.round(interpolate(ndvi, -0.2, 0.0, 0, 200));
        return [r, g, 0];
    }
    if (ndvi < 0.2) {
        let r = Math.round(interpolate(ndvi, 0.0, 0.2, 255, 255));
        let g = Math.round(interpolate(ndvi, 0.0, 0.2, 200, 255));
        return [r, g, 0];
    }
    if (ndvi < 0.4) {
        let r = Math.round(interpolate(ndvi, 0.2, 0.4, 255, 150));
        let g = Math.round(interpolate(ndvi, 0.2, 0.4, 255, 255));
        return [r, g, 0];
    }
    let r = Math.round(interpolate(ndvi, 0.4, 1.0, 150, 0));
    let g = Math.round(interpolate(ndvi, 0.4, 1.0, 255, 255));
    return [r, g, 0];
}

function evaluatePixel(sample) {
    let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    let color = ndviColor(ndvi);
    let alpha = sample.dataMask > 0 ? 255 : 0;
    return [color[0], color[1], color[2], alpha];
}
"""

"use strict";

// Tiny shim exposing the Web Vibration API + a "pause game on
// tab hidden" trigger to the wasm side. Both are no-ops on
// browsers that don't support the feature (so calling
// `test_rpg_vibrate(50)` on iOS Safari, which doesn't ship
// Vibration, silently does nothing).

function platform(importObject) {
    importObject.env.test_rpg_vibrate = function (ms) {
        if (typeof navigator !== "undefined" && navigator.vibrate) {
            try {
                navigator.vibrate(Math.max(0, Math.min(ms, 2000)));
            } catch (e) {
                /* swallow - some browsers reject mid-page-transition */
            }
        }
    };

    // True iff the document is currently visible. Reading this
    // each frame lets the wasm side pause its sim when the user
    // backgrounds the tab (browsers throttle requestAnimationFrame
    // to ~1Hz on backgrounded tabs anyway, but reading the flag
    // lets us skip the sim outright and preserve player state).
    importObject.env.test_rpg_document_visible = function () {
        if (typeof document === "undefined") return 1;
        return document.hidden ? 0 : 1;
    };
}

miniquad_add_plugin({ register_plugin: platform });

// Best-effort auto-save trigger: when the page is about to be
// frozen / unloaded (mobile browsers do this aggressively), nudge
// the wasm to flush a snapshot to localStorage. The wasm side
// exports `test_rpg_request_autosave` if it wants the hook; we
// no-op if it isn't there yet.
window.addEventListener("pagehide", () => {
    if (
        typeof wasm_exports !== "undefined" &&
        wasm_exports &&
        typeof wasm_exports.test_rpg_request_autosave === "function"
    ) {
        try {
            wasm_exports.test_rpg_request_autosave();
        } catch (e) {
            /* swallow */
        }
    }
});

"use strict";

// Audio unlock shim for Android Chrome (and other strict browsers).
//
// macroquad's bundled audio plugin lazily creates its AudioContext
// inside `audio_init`, which runs when Rust first touches the audio
// system. On boot we call `load_tracks` *before* the player has
// tapped the screen, so by the time the gesture listeners are wired
// up the page has already received its first touch and they never
// fire -> the context stays suspended -> no music.
//
// We fix this by wrapping `AudioContext` / `webkitAudioContext`
// constructors *before* mq_js_bundle.js loads so every context the
// macroquad plugin creates gets tracked. A global pool of capture-
// phase gesture listeners stays attached on `window` until every
// tracked context reaches the `running` state, calling `.resume()`
// on each user interaction.

(function () {
    if (typeof window === "undefined") return;

    const Native = window.AudioContext || window.webkitAudioContext;
    if (!Native) return;

    const contexts = [];

    function tryResumeAll() {
        let allRunning = contexts.length > 0;
        for (const ctx of contexts) {
            if (ctx.state !== "running") {
                allRunning = false;
                try {
                    ctx.resume();
                } catch (e) {
                    /* swallow - some browsers throw when called pre-gesture */
                }
            }
        }
        if (allRunning) detachListeners();
    }

    const GESTURE_EVENTS = [
        "touchstart",
        "touchend",
        "pointerdown",
        "mousedown",
        "click",
        "keydown",
    ];

    function onGesture() {
        // Defer one tick so the browser has marked the gesture as
        // user-activated; Chrome occasionally rejects resume() called
        // synchronously inside the very first listener.
        setTimeout(tryResumeAll, 0);
    }

    let attached = false;
    function attachListeners() {
        if (attached) return;
        attached = true;
        for (const evt of GESTURE_EVENTS) {
            window.addEventListener(evt, onGesture, {
                capture: true,
                passive: true,
            });
        }
    }

    function detachListeners() {
        if (!attached) return;
        attached = false;
        for (const evt of GESTURE_EVENTS) {
            window.removeEventListener(evt, onGesture, { capture: true });
        }
    }

    function Wrapped(...args) {
        const ctx = new Native(...args);
        contexts.push(ctx);
        attachListeners();
        // The very first creation already counts as the gesture in
        // some browsers (if the user has interacted prior to this
        // script running); try once eagerly.
        setTimeout(tryResumeAll, 0);
        ctx.addEventListener &&
            ctx.addEventListener("statechange", () => {
                if (contexts.every((c) => c.state === "running")) {
                    detachListeners();
                }
            });
        return ctx;
    }
    Wrapped.prototype = Native.prototype;

    window.AudioContext = Wrapped;
    if (window.webkitAudioContext) {
        window.webkitAudioContext = Wrapped;
    }
})();

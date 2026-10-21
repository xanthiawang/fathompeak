# 沐仞 · 版画交互预览

User-selected artwork: `selected-original.png`, generated with built-in ImageGen and selected on 2026-10-14. Exact generation prompt is in `imagegen-prompt.md`. The original remains unchanged; the website uses a WebP encoding of it, with its full composition and lettering intact.

## Open

- Focused preview: http://127.0.0.1:8766/design/login-engraved-motion_2026-10-14/
- Login context: http://127.0.0.1:8766/#login
- Registration uses the same artwork and interaction module.

## Interaction

- Revision 2 keeps the approved image fixed and makes its added ink behave like an elastic field: nine wind strands respond to pointer proximity and a damped spring.
- Moving over the print leaves three short blue/purple ink trails, which disappear within 950 ms. Trails are bounded to 40 sampled points and masked away from the main lettering and hand silhouette.
- Hold and drag the handshake to tension the wind strands. Release sends a travelling wave through the field; its strength depends on hold duration and drag distance. A short tap produces a lighter response.
- Keyboard: hold Space to build tension and release it to send the wave; Enter gives a short response; Escape cancels a grip. Pointer capture retains the grip outside the hotspot, and pointer cancellation clears it.
- There is no playback button. The print is static until pointer or keyboard interaction; each gesture starts a short animation window, then settles. The former session-storage pause preference is no longer read.
- Focus inside the login/registration form pauses motion until focus leaves the form. Inactive routes, offscreen artwork and hidden browser tabs stop their timelines and animation frames, clear trails and cancel any held grip.
- Reduced-motion preference keeps the static artwork and hides animation controls. The regular mobile login retains its existing form-first layout; the focused preview displays the artwork on mobile and supports tapping the handshake.

## Revision 3: remove playback controls

- Removed the playback button and its styles from login, registration and the focused preview. Removed the infinite ambient animation; the frame loop runs only during a gesture and its brief settling period.
- Browser verification: no playback elements remain on either account route; Enter starts a release and returns to `running=false`; a real pointer drag released at strength 0.99 and then returned to idle. Focusing the email field immediately stopped the animation. No browser errors or warnings observed.
- Motion module syntax and `git diff --check` passed. The module URL is versioned so the old button-dependent script is not reused from cache.

## Implementation

Canonical component markup/styles: `../../index.html`.

Shared motion module: `../../art/account/engraved-motion_2026-10-14.js`. It loads the vendored GSAP runtime only when artwork becomes visible and motion is allowed. A failed runtime load leaves the static image readable. Source image and typography are not regenerated or deformed.

Preview uses the same markup/styles and motion module. It has no account submission functionality. GSAP 3.15.0 runtime and license notice are preserved in `../../vendor/gsap-3.15.0/`.

## Revision 2 checks

- New module passes Node syntax checking; `git diff --check` passes.
- Actual browser pointer drag triggered one release with strength 1.25. A quick tap produced 0.35; a 1.2-second Space hold produced 0.95, confirming that the gesture affects the response. These are interaction parameters, not performance measurements.
- Pause clears trails and tension paths, cancels the grip, stops the frame loop and holds the ribbon geometry unchanged across observations. Play resumes it.
- Desktop login at 1280 × 800: input focus stops the artwork, blur restarts it, no horizontal overflow.
- Narrow login at 365 × 568: artwork is hidden and not initialized; the dedicated preview still supports the grip at this width. Viewport override reset after checks.
- No browser errors or warnings observed. Current screenshots: `interaction-v2-preview.png`, `pull-release-preview.png`.
- Reduced-motion, pointer-cancel and resource-error paths reviewed in code; not forced in the browser.

## Earlier revision checks

- Node syntax checks passed for the new module and all four executable inline website scripts; `git diff --check` passed.
- Desktop preview and actual login inspected at the default 1280 × 720 viewport: full image composition, readable text, no horizontal overflow.
- Pointer movement changed wind transform and light opacity; handshake click and Enter each triggered the pulse.
- Pause held the stroke offset unchanged across browser observations; play resumed it.
- Form focus paused the artwork; blur resumed it. Switching login to registration stopped the inactive login timeline.
- English toggle updated the animation button and handshake accessible labels.
- Login inspected at 390 × 844: no horizontal overflow, artwork hidden and its timeline stopped. The browser viewport override was reset afterward.
- Reduced-motion and runtime-error fallback paths were reviewed in code, not forced in the browser.

## Published 2026-10-14

- Released to GitHub Pages in commit `a24a5261323d09ec5d52bfca657e2eac6ab2cdf6`, based on remote commit `48974ff016336d78eb0224c853c3089ed6cc82de`. The remote compliance, estimator and order updates were preserved.
- Live login: https://xanthiawang.github.io/fathompeak-site/#login
- Live registration: https://xanthiawang.github.io/fathompeak-site/#start
- Pages reported `built` for the release commit. The public HTML, WebP, motion module and GSAP runtime matched the release files by SHA-256.
- Account images are lazy-loaded; visiting the home route did not load the hidden images or initialize their animations.
- The public login and registration artwork each responded to Enter with one release at strength 0.70. Switching routes stopped the inactive artwork. No browser errors or warnings were observed.
- Desktop and narrow layouts were checked; the browser viewport override was reset afterward. Public desktop screenshot: `published-login_2026-10-14.png`.
- Only the five production files were published. Earlier design explorations remain local. The selected source image was not changed in revision 2.

Reference API documentation: https://gsap.com/docs/v3/GSAP/Timeline/ and https://gsap.com/docs/v3/GSAP/Timeline/pause%28%29/

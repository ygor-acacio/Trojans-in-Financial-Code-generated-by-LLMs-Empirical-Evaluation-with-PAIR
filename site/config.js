/* ------------------------------------------------------------------ *
 *  Site configuration
 *
 *  demoEnabled: controls the interactive "Demonstration" tab.
 *
 *     false  ->  the Demonstration tab shows an "offline" notice.
 *     true   ->  the interactive (offline, replay-only) demo is shown.
 *
 *  To turn the demo on, change the line below to `demoEnabled: true`,
 *  commit and push. To turn it off again, set it back to false.
 *
 *  Note: this site is fully static. The demo never calls any AI model
 *  and never runs any code — it only replays results that were already
 *  recorded during the experiment. So there is no usage cost either way;
 *  the flag is just so you decide when the demo is publicly visible.
 * ------------------------------------------------------------------ */
window.SITE_CONFIG = {
  demoEnabled: false
};

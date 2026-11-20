# Project site (GitHub Pages)

A small static site about the project — no build step, no framework, no backend.
Everything is plain HTML/CSS/JS in this `docs/` folder.

```
docs/
├─ index.html          the whole site (tabs: Overview, Problem, Approach, Results, Demonstration, About)
├─ styles.css          styling (light + dark, follows the viewer's system theme)
├─ app.js              tab navigation + the offline demo logic
├─ config.js           ← the one file you edit to turn the demo on/off
├─ data/demo_data.json pre-recorded samples + agent verdicts the demo replays
└─ assets/*.png        figures
```

## Publish it on GitHub Pages

1. Put this project (with the `docs/` folder) in a GitHub repository.
2. On GitHub: **Settings → Pages**.
3. Under **Build and deployment**, set **Source = Deploy from a branch**,
   **Branch = main** (or your default branch) and **Folder = /docs**. Save.
4. After a minute the site is live at
   `https://<your-user>.github.io/<your-repo>/`.

No GitHub Actions and no Jekyll are needed (the `.nojekyll` file disables Jekyll).

## Turn the Demonstration on or off

The interactive demo is **off by default**. The other tabs are always visible.

Open **`docs/config.js`** and change one line:

```js
window.SITE_CONFIG = {
  demoEnabled: false   // ← set to true to show the demo, false to hide it
};
```

Commit and push. With `false`, the Demonstration tab shows a short "offline" notice.
With `true`, the full interactive walkthrough appears.

**There is no usage cost either way.** The demo is a *replay*: it never calls any AI
model and never runs any code in the browser — it only shows samples and agent verdicts
that were already recorded during the experiment (`data/demo_data.json`). The flag just
lets you decide when the demo is publicly visible.

## Regenerate the demo data (optional)

`data/demo_data.json` was generated from the experiment results. To rebuild it:

```bash
python FinalExperiment/analysis/site_build_demo_data.py FinalExperiment/data docs/data/demo_data.json
```

For each (task × complexity × generator) cell it picks a representative recorded sample
and bundles that sample's code together with the three agents' cached verdicts, so the
code shown and the verdicts shown always belong to the same sample. It prefers samples
whose source has no self-labeling comments.

## Edit the text

All copy lives in `index.html`. People, advisors and the repository link are in the
**About** section near the bottom.

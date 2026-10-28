# LPA Projects page "Show details" toggle

paninski-lab/lightning-pose-app#180, PR paninski-lab/lightning-pose-app#181 (branch `feat/project-details-toggle`).

## Behavior

A **Show details** toggle (DaisyUI `toggle`) sits next to **New Project** on the Projects page (`home-page/`).

- **On** (default): project cards are unchanged.
- **Off**: each card shows the project name and the Sessions / Labels / Models stats row only. Data Dir, Model Dir, Views, Keypoints and Labeling Progress are hidden. A stats error line and the card's options menu (Update Paths, Delete) still show.
- The page section is `w-full max-w-5xl`, so it keeps its width when the cards get smaller. With details off, the card grid adds `lg:grid-cols-3` (three cards per row at 1024px and up); below that it stays at two columns (one on narrow screens).

The choice is stored in browser `localStorage` under `showProjectDetails` (`LocalStorageService.showProjectDetails`), so it survives reloads. Anything other than `"false"` means on.

## Tests

`home-page.component.spec.ts`: turning the toggle off hides the paths, views, keypoints and labeling progress, keeps the name and stats row, and writes `showProjectDetails=false`. Width and columns: "keeps the page width and uses three columns on wide screens with details off".

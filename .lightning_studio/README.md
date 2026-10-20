# Lightning Studio hooks

- `on_start.sh` / `on_stop.sh` run on Studio machine start/stop (not on WSL).
- `.studiorc` is created by Lightning Studio under `$HOME/.lightning_studio/` on the cloud machine. It is **not** checked into this repo (Studio-only). A broken `.studiorc` symlink in a WSL clone can be deleted safely.

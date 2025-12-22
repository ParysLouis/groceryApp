# Quick launch guide

This guide helps someone new run the Grocery Planner locally with the fewest possible steps.

## Fast path: single Bash command (Linux/macOS)
From the project root, copy-paste this command. It installs dependencies if needed, starts the dev server, and opens your browser automatically.

```bash
bash scripts/launch-linux.sh   # on Linux
# or
bash scripts/launch-mac.sh     # on macOS
```

The scripts default to port `3000`. To use a different port, set `PORT=4000` (for example) before running the script. The app will open at `http://localhost:<PORT>`.

## Windows (PowerShell)
Run the Windows launcher from the project root:

```powershell
./scripts/launch-windows.ps1
```

## What the launchers do
1. Install dependencies if `node_modules` is missing.
2. Start `npm run dev` bound to `0.0.0.0` so it is reachable from the host or containers.
3. Wait a few seconds and open the browser to the running app.

## Manual alternative
If you prefer to start things yourself, run:

```bash
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Then visit http://localhost:3000. The included SQLite database (`prisma/dev.db`) already contains aisles, units, and seasons.

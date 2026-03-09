# Legacy Vite Archive

Archived Vite SPA code. Kept for reference/rollback. Not used in production Next.js app.

Contents:
- Legacy Vite entry/config (`index.html`, `vite.config.js`)
- Legacy SPA router entry (`src/App.jsx`, `src/main.jsx`)
- Legacy pages (`src/_vite_pages/`)
- Legacy navbar (`src/components/Navbar.jsx`)
- Migration helper scripts (`migrate_*.js`)
- Archived Vite-era tests (`src/test/`) that depended on `react-router-dom` + `../pages/*`
- CSS rollback snapshots and selector inventory (`css_snapshot/`)

Notes:
- This folder is intentionally archived instead of deleted.
- Active production frontend uses Next.js App Router (`app/`) and shared modules under `src/`.

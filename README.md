# Focus Timer

A Pomodoro-style focus timer in two flavours: a terminal app and a browser page.

## Usage

### Browser (`timer.html`)

Open `timer.html` directly in any browser — no server needed.

- Click **START** or press `Space` to begin
- Press `1` / `2` / `3` to switch between Focus (25 min), Short break (5 min), and Long break (15 min)
- Press `R` to reset
- Stats and streaks are stored in `localStorage`

### Terminal (`timer.py`)

Requires Python 3.8+ on Windows (uses `msvcrt`).

```bash
python timer.py
```

- Press `1`, `2`, or `3` to pick a session type
- `Space` to pause/resume, `Q` to quit
- Streaks are saved to `streaks.json` next to the script

## Sessions

| Mode        | Duration |
|-------------|----------|
| Focus       | 25 min   |
| Short break | 5 min    |
| Long break  | 15 min   |

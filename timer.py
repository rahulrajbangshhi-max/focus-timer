import time
import json
import os
import sys
import datetime
import msvcrt

DATA_FILE = os.path.join(os.path.dirname(__file__), "streaks.json")

SESSIONS = {
    "work":  {"label": "Focus",       "minutes": 25, "color": "\033[92m"},
    "short": {"label": "Short break", "minutes":  5, "color": "\033[94m"},
    "long":  {"label": "Long break",  "minutes": 15, "color": "\033[95m"},
}

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"

BAR_WIDTH = 30


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"streak": 0, "last_date": None, "total_sessions": 0, "today_sessions": 0, "today_date": None}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_streak(data):
    today = str(datetime.date.today())
    if data["today_date"] != today:
        data["today_sessions"] = 0
        data["today_date"] = today

    data["today_sessions"] += 1
    data["total_sessions"] += 1

    last = data["last_date"]
    if last is None:
        data["streak"] = 1
    else:
        last_dt = datetime.date.fromisoformat(last)
        delta = datetime.date.today() - last_dt
        if delta.days == 1:
            data["streak"] += 1
        elif delta.days == 0:
            pass  # same day, streak unchanged
        else:
            data["streak"] = 1

    data["last_date"] = today
    save_data(data)


def progress_bar(elapsed, total, color):
    pct = elapsed / total
    filled = int(BAR_WIDTH * pct)
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    return f"{color}[{bar}]{RESET} {int(pct * 100):3d}%"


def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def flame(streak):
    if streak >= 7:
        return f"{YELLOW}{BOLD}🔥×{streak}{RESET}"
    elif streak >= 3:
        return f"{YELLOW}🔥×{streak}{RESET}"
    elif streak >= 1:
        return f"🔥×{streak}"
    return ""


def kbhit_nonblock():
    if os.name == "nt":
        return msvcrt.kbhit()
    import select
    return select.select([sys.stdin], [], [], 0)[0]


def get_key():
    if os.name == "nt":
        return msvcrt.getwch()
    return sys.stdin.read(1)


def run_session(kind, data):
    cfg = SESSIONS[kind]
    label = cfg["label"]
    color = cfg["color"]
    total = cfg["minutes"] * 60
    start = time.time()
    paused = False
    pause_start = None
    pause_total = 0

    while True:
        now = time.time()
        if paused:
            elapsed = pause_start - start - pause_total
        else:
            elapsed = now - start - pause_total

        remaining = total - elapsed

        clear()
        print(f"\n  {BOLD}Focus Timer{RESET}  {flame(data['streak'])}\n")
        print(f"  {color}{BOLD}{label}{RESET}  —  {format_time(remaining)} left\n")
        print(f"  {progress_bar(elapsed, total, color)}\n")

        today_label = f"today: {data['today_sessions']} session{'s' if data['today_sessions'] != 1 else ''}"
        total_label = f"total: {data['total_sessions']}"
        print(f"  {DIM}{today_label}  ·  {total_label}{RESET}\n")

        if paused:
            print(f"  {YELLOW}⏸  Paused — press [space] to resume, [q] to quit{RESET}")
        else:
            print(f"  {DIM}[space] pause  ·  [q] quit{RESET}")

        if elapsed >= total:
            break

        if kbhit_nonblock():
            ch = get_key()
            if ch == " ":
                if paused:
                    pause_total += time.time() - pause_start
                    paused = False
                else:
                    pause_start = time.time()
                    paused = True
            elif ch in ("q", "Q"):
                return False  # user quit

        time.sleep(0.5)

    # session complete
    if kind == "work":
        update_streak(data)
        data = load_data()
        clear()
        print(f"\n  {GREEN}{BOLD}✓ Focus session complete!{RESET}  {flame(data['streak'])}\n")
        print(f"  {DIM}Streak: {data['streak']} day{'s' if data['streak'] != 1 else ''}  ·  Today: {data['today_sessions']} session{'s' if data['today_sessions'] != 1 else ''}{RESET}\n")
    else:
        clear()
        print(f"\n  {GREEN}{BOLD}✓ Break done — back to it!{RESET}\n")

    return True


def menu(data):
    clear()
    print(f"\n  {BOLD}Focus Timer{RESET}  {flame(data['streak'])}\n")
    streak_line = f"Day streak: {data['streak']}" if data["streak"] > 0 else "No streak yet"
    print(f"  {DIM}{streak_line}  ·  Total sessions: {data['total_sessions']}{RESET}\n")
    print(f"  {BOLD}[1]{RESET} Focus session    {DIM}25 min{RESET}")
    print(f"  {BOLD}[2]{RESET} Short break       {DIM}5 min{RESET}")
    print(f"  {BOLD}[3]{RESET} Long break        {DIM}15 min{RESET}")
    print(f"  {BOLD}[q]{RESET} Quit\n")
    print(f"  {DIM}Press a key...{RESET}", end="", flush=True)

    while True:
        if kbhit_nonblock():
            ch = get_key()
            if ch == "1":
                return "work"
            elif ch == "2":
                return "short"
            elif ch == "3":
                return "long"
            elif ch in ("q", "Q"):
                return None
        time.sleep(0.1)


def main():
    if os.name != "nt":
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        while True:
            data = load_data()
            choice = menu(data)
            if choice is None:
                clear()
                print(f"\n  {DIM}See you tomorrow. Keep the streak alive!{RESET}\n")
                break
            result = run_session(choice, data)
            if not result:
                break
            input("\n  Press Enter to continue...")
    finally:
        if os.name != "nt":
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


if __name__ == "__main__":
    main()

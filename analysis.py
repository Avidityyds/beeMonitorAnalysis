from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # for environments without display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import HourLocator

DATA_DIR = Path("data")
OUT_DIR = Path("output")


def load_latest_month_csv() -> pd.DataFrame:
    """Load the latest *_TX2_6_inout.csv file from data/ folder."""
    files = sorted(DATA_DIR.glob("*_TX2_6_inout.csv"))
    if not files:
        raise FileNotFoundError("No *_TX2_6_inout.csv found in data/")

    csv_path = files[-1]
    print(f"[INFO] Using input file: {csv_path}")
    df = pd.read_csv(csv_path)

    # Handle alternative column names
    rename_map = {}
    if "inpollen" in df.columns:
        rename_map["inpollen"] = "in_pollen"
    if "outpollen" in df.columns:
        rename_map["outpollen"] = "out_pollen"
    if rename_map:
        df = df.rename(columns=rename_map)

    need_cols = [
        'dt', 'in_worker', 'out_worker',
        'in_pollen', 'out_pollen',
        'in_drone', 'out_drone'
    ]

    missing = [c for c in need_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Auto-calculate pollen_rate if missing
    if 'pollen_rate' not in df.columns:
        print("[INFO] pollen_rate not found, calculating automatically...")
        total_in = df['in_worker'] + df['in_pollen'] + df['in_drone']
        pollen_in = df['in_pollen']
        df['pollen_rate'] = pollen_in / total_in.replace(0, pd.NA)

    # Parse datetime
    for fmt in (None, "%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M"):
        try:
            if fmt is None:
                df["dt"] = pd.to_datetime(
                    df["dt"], errors="raise", infer_datetime_format=True
                )
            else:
                df["dt"] = pd.to_datetime(df["dt"], format=fmt)
            break
        except Exception:
            continue
    else:
        raise ValueError("Cannot parse dt datetime format")

    df = df.sort_values("dt").reset_index(drop=True)
    return df


def filter_by_day_range(df: pd.DataFrame, day_start: int, day_end: int) -> pd.DataFrame:
    """Filter data by day-of-month range, e.g., day 1–10."""
    dff = df[(df["dt"].dt.day >= day_start) & (df["dt"].dt.day <= day_end)].copy()
    print(f"[INFO] Day {day_start:02d}-{day_end:02d}: {len(dff)} rows")
    return dff


def plot_inout_window(dff: pd.DataFrame, day_label: str):
    """Plot bee in/out counts with 6-hour x-axis ticks."""
    if dff.empty:
        print(f"[WARN] inout {day_label} no data, skip")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Worker bees
    ax.plot(dff["dt"], dff["in_worker"], label="Worker IN (in_worker)", color="tab:blue", linewidth=1.5)
    ax.plot(dff["dt"], dff["out_worker"], label="Worker OUT (out_worker)", color="tab:blue", linestyle="--", linewidth=1.5)

    # Pollen workers
    ax.plot(dff["dt"], dff["in_pollen"], label="Pollen worker IN (in_pollen)", color="orange", linewidth=1.5)
    ax.plot(dff["dt"], dff["out_pollen"], label="Pollen worker OUT (out_pollen)", color="orange", linestyle="--", linewidth=1.5)

    # Drones
    ax.plot(dff["dt"], dff["in_drone"], label="Drone IN (in_drone)", color="red", linewidth=1.5)
    ax.plot(dff["dt"], dff["out_drone"], label="Drone OUT (out_drone)", color="red", linestyle="--", linewidth=1.5)

    ax.set_title(f"{day_label} day window: Bee in/out counts")
    ax.set_xlabel("Time (24-hour)")
    ax.set_ylabel("Count")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    # --- 6-hour ticks ---
    ax.xaxis.set_major_locator(HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"inout_{day_label}.png"

    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved figure: {out_path}")


def plot_pollen_window(dff: pd.DataFrame, day_label: str):
    """Plot pollen ratio with 6-hour x-axis ticks."""
    if dff.empty:
        print(f"[WARN] pollen {day_label} no data, skip")
        return

    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        dff["dt"],
        dff["pollen_rate"].astype(float),
        label="Pollen ratio",
        color="green",
        linewidth=1.5,
    )

    ax.set_title(f"{day_label} day window: Pollen ratio")
    ax.set_xlabel("Time (24-hour)")
    ax.set_ylabel("Pollen ratio")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    # --- 6-hour ticks ---
    ax.xaxis.set_major_locator(HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"pollen_{day_label}.png"

    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved figure: {out_path}")


def main():
    print("[INFO] Start 10-day window analysis...")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_latest_month_csv()

    # Get last day of this month
    last_day = df["dt"].dt.day.max()

    windows = [
        (1, 10, "01-10"),
        (11, 20, "11-20"),
        (21, last_day, f"21-{last_day:02d}"),
    ]

    for day_start, day_end, label in windows:
        dff = filter_by_day_range(df, day_start, day_end)
        plot_inout_window(dff, label)
        plot_pollen_window(dff, label)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()

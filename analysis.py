from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # for GitHub Actions / 沒有螢幕的環境用
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_DIR = Path("data")
OUT_DIR = Path("output")

# 期望的欄位：
# dt, in_worker, out_worker, in_pollen, out_pollen, in_drone, out_drone, pollen_rate


def load_latest_month_csv() -> pd.DataFrame:
    """從 data/ 底下找最新一個 *_TX2_6_inout.csv，讀進 DataFrame。"""
    files = sorted(DATA_DIR.glob("*_TX2_6_inout.csv"))
    if not files:
        raise FileNotFoundError("data/ 資料夾內找不到任何 *_TX2_6_inout.csv 檔案")

    csv_path = files[-1]
    print(f"[INFO] Using input file: {csv_path}")
    df = pd.read_csv(csv_path)

    # 有些版本欄位可能是 inpollen / outpollen
    rename_map = {}
    if "inpollen" in df.columns:
        rename_map["inpollen"] = "in_pollen"
    if "outpollen" in df.columns:
        rename_map["outpollen"] = "out_pollen"
    if rename_map:
        df = df.rename(columns=rename_map)

    need_cols = [
        "dt",
        "in_worker", "out_worker",
        "in_pollen", "out_pollen",
        "in_drone", "out_drone",
        "pollen_rate",
    ]
    missing = [c for c in need_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少欄位：{missing}\n期待欄位：{need_cols}")

    # 解析時間欄位 dt
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
        raise ValueError("無法解析 dt 欄位的時間格式")

    df = df.sort_values("dt").reset_index(drop=True)
    return df


def setup_chinese_font():
    """盡量設定中文字型（失敗就算了，不影響程式跑）。"""
    try:
        matplotlib.rc("font", family="Arial Unicode Ms")
    except Exception:
        pass


def filter_by_day_range(df: pd.DataFrame, day_start: int, day_end: int) -> pd.DataFrame:
    """根據日期中的 day 篩選資料，例如 1–10 號。"""
    dff = df[(df["dt"].dt.day >= day_start) & (df["dt"].dt.day <= day_end)].copy()
    print(f"[INFO] Day {day_start:02d}-{day_end:02d}: {len(dff)} rows")
    return dff


def plot_inout_window(dff: pd.DataFrame, day_label: str):
    """畫進出量 6 條線，儲存成 inout_<label>.png。"""
    if dff.empty:
        print(f"[WARN] inout {day_label} 沒有資料，略過畫圖")
        return

    setup_chinese_font()

    fig, ax = plt.subplots(figsize=(12, 6))

    # 工蜂：藍色
    ax.plot(
        dff["dt"],
        dff["in_worker"],
        label="工蜂進巢 (in_worker)",
        color="tab:blue",
        linewidth=1.5,
    )
    ax.plot(
        dff["dt"],
        dff["out_worker"],
        label="工蜂出巢 (out_worker)",
        color="tab:blue",
        linestyle="--",
        linewidth=1.5,
    )

    # 花粉工蜂：橘色
    ax.plot(
        dff["dt"],
        dff["in_pollen"],
        label="花粉工蜂進巢 (in_pollen)",
        color="orange",
        linewidth=1.5,
    )
    ax.plot(
        dff["dt"],
        dff["out_pollen"],
        label="花粉工蜂出巢 (out_pollen)",
        color="orange",
        linestyle="--",
        linewidth=1.5,
    )

    # 雄蜂：紅色
    ax.plot(
        dff["dt"],
        dff["in_drone"],
        label="雄蜂進巢 (in_drone)",
        color="red",
        linewidth=1.5,
    )
    ax.plot(
        dff["dt"],
        dff["out_drone"],
        label="雄蜂出巢 (out_drone)",
        color="red",
        linestyle="--",
        linewidth=1.5,
    )

    ax.set_title(f"{day_label} 日區間：各類蜜蜂進出量")
    ax.set_xlabel("時間")
    ax.set_ylabel("數量")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    # X 軸用日期＋時間
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
    plt.setp(ax.get_xticklabels(), rotation=0)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"inout_{day_label}.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved figure: {out_path}")


def plot_pollen_window(dff: pd.DataFrame, day_label: str):
    """畫花粉率折線圖，儲存成 pollen_<label>.png。"""
    if dff.empty:
        print(f"[WARN] pollen {day_label} 沒有資料，略過畫圖")
        return

    setup_chinese_font()

    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        dff["dt"],
        dff["pollen_rate"].astype(float),
        label="花粉率",
        color="green",
        linewidth=1.5,
    )

    ax.set_title(f"{day_label} 日區間：花粉率變化")
    ax.set_xlabel("時間")
    ax.set_ylabel("花粉率")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
    plt.setp(ax.get_xticklabels(), rotation=0)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"pollen_{day_label}.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved figure: {out_path}")


def main():
    print("[INFO] Start monthly window analysis...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_latest_month_csv()

    # 取出這個月的最後一天 (28 / 30 / 31)
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

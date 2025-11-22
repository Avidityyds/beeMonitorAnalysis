from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUT_DIR = Path("output")

def main():
    print("Start analysis...")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    input_file = DATA_DIR / "input.csv"

    if not input_file.exists():
        print("No input.csv found, create dummy data")
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4, 5, 6]
        })
    else:
        df = pd.read_csv(input_file)

    df["sum"] = df["a"] + df["b"]

    out_file = OUT_DIR / "result.csv"
    df.to_csv(out_file, index=False)
    print(f"Saved result to {out_file}")

if __name__ == "__main__":
    main()

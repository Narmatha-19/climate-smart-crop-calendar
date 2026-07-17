import os
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FOLDER = "../../dataset/processed"
OUTPUT_FOLDER = "../../output/graphs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

files = os.listdir(INPUT_FOLDER)

for file in files:

    if not file.endswith(".csv"):
        continue

    district = file.replace(".csv", "")

    print(f"Generating graphs for {district}")

    df = pd.read_csv(os.path.join(INPUT_FOLDER, file))

    df["Date"] = pd.to_datetime(df["Date"])
    # Extract Year and Month from Date
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.strftime("%b")

    district_folder = os.path.join(OUTPUT_FOLDER, district)
    os.makedirs(district_folder, exist_ok=True)

    month_order = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

    df["Month"] = pd.Categorical(
        df["Month"],
        categories=month_order,
        ordered=True
    )

    # -------------------------
    # Daily Temperature
    # -------------------------

    plt.figure(figsize=(12,5))
    plt.plot(df["Date"], df["Temperature"], color="blue")
    plt.title(f"{district} Daily Temperature")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "Temperature.png"))
    plt.close()

    # -------------------------
    # Daily Rainfall
    # -------------------------

    plt.figure(figsize=(12,5))
    plt.plot(df["Date"], df["Rainfall"], color="green")
    plt.title(f"{district} Daily Rainfall")
    plt.xlabel("Date")
    plt.ylabel("Rainfall (mm)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "Rainfall.png"))
    plt.close()

    # -------------------------
    # Humidity
    # -------------------------

    plt.figure(figsize=(12,5))
    plt.plot(df["Date"], df["Humidity"], color="orange")
    plt.title(f"{district} Daily Humidity")
    plt.xlabel("Date")
    plt.ylabel("Humidity (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "Humidity.png"))
    plt.close()

    # -------------------------
    # Wind Speed
    # -------------------------

    plt.figure(figsize=(12,5))
    plt.plot(df["Date"], df["WindSpeed"], color="purple")
    plt.title(f"{district} Daily Wind Speed")
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "WindSpeed.png"))
    plt.close()

    # -------------------------
    # Monthly Rainfall
    # -------------------------

    monthly_rain = df.groupby("Month")["Rainfall"].mean()

    plt.figure(figsize=(8,5))
    monthly_rain.plot(kind="bar", color="green")
    plt.title(f"{district} Average Monthly Rainfall")
    plt.xlabel("Month")
    plt.ylabel("Rainfall")
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "MonthlyRainfall.png"))
    plt.close()

    # -------------------------
    # Monthly Temperature
    # -------------------------

    monthly_temp = df.groupby("Month")["Temperature"].mean()

    plt.figure(figsize=(8,5))
    monthly_temp.plot(kind="bar", color="red")
    plt.title(f"{district} Average Monthly Temperature")
    plt.xlabel("Month")
    plt.ylabel("Temperature")
    plt.tight_layout()
    plt.savefig(os.path.join(district_folder, "MonthlyTemperature.png"))
    plt.close()

print("\nAll Graphs Generated Successfully!")
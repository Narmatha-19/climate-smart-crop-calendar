import os
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "output",
    "analysis",
    "tables",
    "district_statistics.csv"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "analysis",
    "figures",
    "spatial"
)

TABLE_FOLDER = os.path.join(
    BASE_DIR,
    "output",
    "analysis",
    "tables"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =====================================================
# READ DATA
# =====================================================

df = pd.read_csv(INPUT_FILE)

# =====================================================
# SORT DATA
# =====================================================

temp_df = df.sort_values("Average Temperature", ascending=False)

rain_df = df.sort_values("Average Rainfall", ascending=False)

humidity_df = df.sort_values("Average Humidity", ascending=False)

wind_df = df.sort_values("Average WindSpeed", ascending=False)

# =====================================================
# FUNCTION TO SAVE BAR CHART
# =====================================================

def save_chart(data, x, y, title, filename):

    plt.figure(figsize=(14,6))

    plt.bar(data[x], data[y])

    plt.xticks(rotation=90)

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_FOLDER,
            filename
        ),
        dpi=300
    )

    plt.close()

# =====================================================
# CREATE CHARTS
# =====================================================

save_chart(
    temp_df,
    "District",
    "Average Temperature",
    "Average Temperature by District",
    "average_temperature.png"
)

save_chart(
    rain_df,
    "District",
    "Average Rainfall",
    "Average Rainfall by District",
    "average_rainfall.png"
)

save_chart(
    humidity_df,
    "District",
    "Average Humidity",
    "Average Humidity by District",
    "average_humidity.png"
)

save_chart(
    wind_df,
    "District",
    "Average WindSpeed",
    "Average Wind Speed by District",
    "average_windspeed.png"
)

# =====================================================
# TOP 10 DISTRICTS
# =====================================================

top10_hot = temp_df.head(10)

top10_rain = rain_df.head(10)

top10_hot.to_csv(
    os.path.join(
        TABLE_FOLDER,
        "top10_hottest.csv"
    ),
    index=False
)

top10_rain.to_csv(
    os.path.join(
        TABLE_FOLDER,
        "top10_rainfall.csv"
    ),
    index=False
)

save_chart(
    top10_hot,
    "District",
    "Average Temperature",
    "Top 10 Hottest Districts",
    "top10_hottest.png"
)

save_chart(
    top10_rain,
    "District",
    "Average Rainfall",
    "Top 10 Rainfall Districts",
    "top10_rainfall.png"
)

# =====================================================
# AUTOMATIC INSIGHTS
# =====================================================

highest_temp = temp_df.iloc[0]
lowest_temp = temp_df.iloc[-1]

highest_rain = rain_df.iloc[0]
lowest_rain = rain_df.iloc[-1]

report = os.path.join(
    BASE_DIR,
    "output",
    "analysis",
    "summary",
    "spatial_insights.txt"
)

with open(report,"w") as f:

    f.write("SPATIAL CLIMATE ANALYSIS\n\n")

    f.write(f"Hottest District : {highest_temp['District']}\n")
    f.write(f"Average Temperature : {highest_temp['Average Temperature']} °C\n\n")

    f.write(f"Coolest District : {lowest_temp['District']}\n")
    f.write(f"Average Temperature : {lowest_temp['Average Temperature']} °C\n\n")

    f.write(f"Highest Rainfall District : {highest_rain['District']}\n")
    f.write(f"Average Rainfall : {highest_rain['Average Rainfall']} mm/day\n\n")

    f.write(f"Lowest Rainfall District : {lowest_rain['District']}\n")
    f.write(f"Average Rainfall : {lowest_rain['Average Rainfall']} mm/day\n")

print("\nSpatial Analysis Completed Successfully!")
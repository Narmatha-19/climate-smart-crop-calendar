import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ======================================================
# PATHS
# ======================================================

INPUT_FILE = "../../output/climate_intelligence/yearly_summary.csv"

GRAPH_FOLDER = "../../output/climate_intelligence/temperature_trends"

REPORT_FOLDER = "../../output/climate_intelligence/reports"

os.makedirs(GRAPH_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ======================================================
# READ DATA
# ======================================================

df = pd.read_csv(INPUT_FILE)

results = []

districts = df["District"].unique()

print("=" * 50)
print("TEMPERATURE TREND ANALYSIS")
print("=" * 50)

# ======================================================
# PROCESS EACH DISTRICT
# ======================================================

for district in districts:

    district_df = df[df["District"] == district].copy()

    district_df = district_df.sort_values("Year")

    start_year = district_df["Year"].min()
    end_year = district_df["Year"].max()

    years = end_year - start_year + 1

    X = district_df["Year"].values.reshape(-1,1)

    y = district_df["AvgTemperature"].values

    # --------------------------------------------
    # Linear Regression
    # --------------------------------------------

    model = LinearRegression()

    model.fit(X,y)

    prediction = model.predict(X)

    slope = model.coef_[0]

    r2 = r2_score(y,prediction)

    # --------------------------------------------
    # Percentage Change
    # --------------------------------------------

    first_temp = y[0]

    last_temp = y[-1]

    percentage_change = (

        (last_temp-first_temp)

        / first_temp

    ) * 100

    # --------------------------------------------
    # Temperature Range
    # --------------------------------------------

    avg_temp_range = (

        district_df["MaxTemperature"]

        -

        district_df["MinTemperature"]

    ).mean()

    # --------------------------------------------
    # Temperature Stability
    # --------------------------------------------

    avg_std = district_df["TemperatureStd"].mean()

    # --------------------------------------------
    # Trend Classification
    # --------------------------------------------

    if slope > 0.08:

        trend = "Increasing"

        strength = "Strong Increase"

    elif slope > 0.03:

        trend = "Increasing"

        strength = "Moderate Increase"

    elif slope >= -0.03:

        trend = "Stable"

        strength = "Stable"

    elif slope >= -0.08:

        trend = "Decreasing"

        strength = "Moderate Decrease"

    else:

        trend = "Decreasing"

        strength = "Strong Decrease"

    # --------------------------------------------
    # Save Result
    # --------------------------------------------

    results.append({

        "District":district,

        "Start Year":start_year,

        "End Year":end_year,

        "Years Analysed":years,

        "Slope":round(slope,4),

        "R2 Score":round(r2,3),

        "Percentage Change (%)":round(percentage_change,2),

        "Average Temperature Range":round(avg_temp_range,2),

        "Temperature Std":round(avg_std,2),

        "Trend":trend,

        "Strength":strength

    })

    # ======================================================
    # GRAPH
    # ======================================================

    plt.figure(figsize=(9,5))

    plt.plot(

        district_df["Year"],

        y,

        marker="o",

        linewidth=2,

        label="Observed Temperature"

    )

    plt.plot(

        district_df["Year"],

        prediction,

        linestyle="--",

        linewidth=2,

        label="Regression Trend"

    )

    plt.title(

        f"{district} District\n"

        f"Temperature Trend Analysis ({start_year}-{end_year})",

        fontsize=13,

        fontweight="bold"

    )

    plt.xlabel("Year")

    plt.ylabel("Average Temperature (°C)")

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig(

        os.path.join(

            GRAPH_FOLDER,

            f"{district}.png"

        ),

        dpi=300

    )

    plt.close()

# ======================================================
# SAVE CSV
# ======================================================

result_df = pd.DataFrame(results)

csv_file = os.path.join(

    REPORT_FOLDER,

    "temperature_trends.csv"

)

result_df.to_csv(

    csv_file,

    index=False

)

# ======================================================
# SUMMARY REPORT
# ======================================================

summary_file = os.path.join(

    REPORT_FOLDER,

    "temperature_summary.txt"

)

with open(summary_file,"w",encoding="utf-8") as report:

    report.write("="*60+"\n")

    report.write("TEMPERATURE TREND ANALYSIS REPORT\n")

    report.write("="*60+"\n\n")

    for _,row in result_df.iterrows():

        report.write(f"District : {row['District']}\n")

        report.write(f"Study Period : {row['Start Year']} - {row['End Year']}\n")

        report.write(f"Years Analysed : {row['Years Analysed']}\n")

        report.write(f"Slope : {row['Slope']}\n")

        report.write(f"R² Score : {row['R2 Score']}\n")

        report.write(f"Percentage Change : {row['Percentage Change (%)']}%\n")

        report.write(f"Average Temperature Range : {row['Average Temperature Range']}°C\n")

        report.write(f"Temperature Std : {row['Temperature Std']}\n")

        report.write(f"Trend : {row['Trend']}\n")

        report.write(f"Strength : {row['Strength']}\n")

        if row["Trend"]=="Increasing":

            interpretation="Average temperature is increasing over the study period."

        elif row["Trend"]=="Decreasing":

            interpretation="Average temperature is decreasing over the study period."

        else:

            interpretation="Average temperature remains relatively stable."

        report.write(f"Interpretation : {interpretation}\n")

        report.write("-"*60+"\n\n")

    report.write("="*60+"\n")

    report.write("RESEARCH OBSERVATIONS\n")

    report.write("="*60+"\n\n")

    report.write("1. Average temperature trend was analysed using Linear Regression.\n")

    report.write("2. Temperature Range indicates daily climate variability.\n")

    report.write("3. Temperature Standard Deviation will contribute to Climate Stability Index.\n")

    report.write("4. Temperature trend is one of the major features for Crop Calendar Recommendation.\n")

print(result_df)

print("\nTemperature Trend Analysis Completed Successfully!")

print(f"\nCSV Saved : {csv_file}")

print(f"Summary Saved : {summary_file}")
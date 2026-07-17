import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ======================================================
# PATHS
# ======================================================

INPUT_FILE = "../../output/climate_intelligence/yearly_summary.csv"

GRAPH_FOLDER = "../../output/climate_intelligence/rainfall_trends"

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
print("RAINFALL TREND ANALYSIS")
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

    X = district_df["Year"].values.reshape(-1, 1)

    y = district_df["TotalRainfall"].values

    # -----------------------------------------
    # Linear Regression
    # -----------------------------------------

    model = LinearRegression()

    model.fit(X, y)

    prediction = model.predict(X)

    slope = model.coef_[0]

    r2 = r2_score(y, prediction)

    # -----------------------------------------
    # Percentage Change
    # -----------------------------------------

    first_rainfall = y[0]
    last_rainfall = y[-1]

    percentage_change = (
        (last_rainfall - first_rainfall)
        / first_rainfall
    ) * 100

    # -----------------------------------------
    # Trend Classification
    # -----------------------------------------

    if slope > 20:

        trend = "Increasing"
        strength = "Strong Increase"

    elif slope > 10:

        trend = "Increasing"
        strength = "Moderate Increase"

    elif slope >= -10:

        trend = "Stable"
        strength = "Stable"

    elif slope >= -20:

        trend = "Decreasing"
        strength = "Moderate Decrease"

    else:

        trend = "Decreasing"
        strength = "Strong Decrease"

    # -----------------------------------------
    # Save Results
    # -----------------------------------------

    results.append({

        "District": district,

        "Start Year": start_year,

        "End Year": end_year,

        "Years Analysed": years,

        "Slope": round(slope, 2),

        "R2 Score": round(r2, 3),

        "Percentage Change (%)": round(percentage_change, 2),

        "Trend": trend,

        "Strength": strength

    })

    # ======================================================
    # GRAPH
    # ======================================================

    plt.figure(figsize=(9, 5))

    plt.plot(

        district_df["Year"],
        y,

        marker="o",

        linewidth=2,

        label="Observed Rainfall"

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
        f"Rainfall Trend Analysis ({start_year}-{end_year})",

        fontsize=13,

        fontweight="bold"

    )

    plt.xlabel("Year")

    plt.ylabel("Annual Rainfall (mm)")

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

    "rainfall_trends.csv"

)

result_df.to_csv(

    csv_file,

    index=False

)

# ======================================================
# GENERATE SUMMARY REPORT
# ======================================================

summary_file = os.path.join(

    REPORT_FOLDER,

    "rainfall_summary.txt"

)

with open(summary_file, "w", encoding="utf-8") as report:

    report.write("=" * 60 + "\n")
    report.write("RAINFALL TREND ANALYSIS REPORT\n")
    report.write("=" * 60 + "\n\n")

    for _, row in result_df.iterrows():

        report.write(f"District : {row['District']}\n")

        report.write(
            f"Study Period : {row['Start Year']} - {row['End Year']}\n"
        )

        report.write(
            f"Years Analysed : {row['Years Analysed']}\n"
        )

        report.write(
            f"Slope : {row['Slope']}\n"
        )

        report.write(
            f"R² Score : {row['R2 Score']}\n"
        )

        report.write(
            f"Percentage Change : {row['Percentage Change (%)']}%\n"
        )

        report.write(
            f"Trend : {row['Trend']}\n"
        )

        report.write(
            f"Strength : {row['Strength']}\n"
        )

        # -------------------------------------

        if row["Trend"] == "Increasing":

            interpretation = (
                "Annual rainfall shows an increasing trend "
                "during the study period."
            )

        elif row["Trend"] == "Decreasing":

            interpretation = (
                "Annual rainfall shows a decreasing trend "
                "during the study period."
            )

        else:

            interpretation = (
                "Annual rainfall remains relatively stable "
                "during the study period."
            )

        report.write(
            f"Interpretation : {interpretation}\n"
        )

        report.write("-" * 60 + "\n\n")

    # ==================================================
    # RESEARCH OBSERVATION
    # ==================================================

    report.write("\n")
    report.write("=" * 60 + "\n")
    report.write("RESEARCH OBSERVATIONS\n")
    report.write("=" * 60 + "\n\n")

    report.write(
        "1. Linear regression was used to analyse long-term rainfall trends.\n"
    )

    report.write(
        "2. Low R² values indicate high year-to-year rainfall variability.\n"
    )

    report.write(
        "3. Rainfall variability is expected to become an important feature "
        "for the Climate Stability Index.\n"
    )

    report.write(
        "4. The generated trend information will be integrated into the "
        "Machine Learning recommendation model.\n"
    )

print(result_df)

print("\nRainfall Trend Analysis Completed Successfully!")

print(f"\nCSV Saved : {csv_file}")

print(f"Summary Report Saved : {summary_file}")
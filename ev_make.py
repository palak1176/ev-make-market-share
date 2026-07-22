import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Arial'

def ev_make_market_share(file_path):
    # Reads Excel file
    try:
        ev_make_market_share_df = pd.read_excel(file_path, header=2)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: There was a parsing error while reading the file.")
        return None
    
    # Check for required columns and keep only those needed for analysis
    columns_to_keep = ["Date Hierarchy - Year", "GVWR Category", "Make", "Registrations"]
    missing_cols = [col for col in columns_to_keep if col not in ev_make_market_share_df.columns]
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        return None
    ev_make_market_share_df = ev_make_market_share_df[columns_to_keep]
    
    # Find number of registrations by make for each year and return a DataFrame with the results
    ev_make_market_share_df = ev_make_market_share_df.groupby(["Date Hierarchy - Year", "GVWR Category", "Make"])["Registrations"].sum().reset_index()

    # All makes that have less than 1% of the total registrations for that year and GVWR category will be grouped into an "Other" category
    totals = ev_make_market_share_df.groupby(["Date Hierarchy - Year", "GVWR Category"])["Registrations"].transform("sum")
    ev_make_market_share_df.loc[ev_make_market_share_df["Registrations"] < 0.01 * totals, "Make"] = "Other"
    ev_make_market_share_df = (ev_make_market_share_df.groupby(["Date Hierarchy - Year", "GVWR Category", "Make"], as_index=False)["Registrations"].sum())

    # Sort the DataFrame by year, GVWR category, make, and registrations in descending order
    ev_make_market_share_df = ev_make_market_share_df.sort_values(["Date Hierarchy - Year", "GVWR Category", "Registrations"], ascending=[True, True, False])

    # Create a consistent color mapping
    unique_makes = sorted(ev_make_market_share_df["Make"].unique())
    colors = np.vstack([
    plt.cm.tab20(np.linspace(0, 1, 20)),
    plt.cm.tab20b(np.linspace(0, 1, 20)),
    plt.cm.tab20c(np.linspace(0, 1, 20))])
    make_colors = dict(zip(unique_makes, colors[:len(unique_makes)]))
    # Optional: always make "Other" gray
    make_colors["Other"] = "lightgray"
    
    # Create pie charts for each year and GVWR category
    for year in ev_make_market_share_df["Date Hierarchy - Year"].unique():
        for gvwr in ev_make_market_share_df["GVWR Category"].unique():
            data = ev_make_market_share_df[(ev_make_market_share_df["Date Hierarchy - Year"] == year) & (ev_make_market_share_df["GVWR Category"] == gvwr)]

            if data.empty:
                print(f"No data available for {year} and {gvwr}.")
                continue
            
            # Get colors for the makes in this chart
            pie_colors = [make_colors[make] for make in data["Make"]]

            plt.figure(figsize=(8, 8))            
            wedges, texts, autotexts = plt.pie(
                data["Registrations"],
                labels=data["Make"],
                colors=pie_colors,
                autopct=lambda p: f'{p:.1f}%' if p >= 3 else '',
                startangle=140)

            # Create a legend for the small slices
            small_mask = data["Registrations"] / data["Registrations"].sum() < 0.03

            small_wedges = [w for w, small in zip(wedges, small_mask) if small]

            small_labels = [
                f"{make} ({reg/data['Registrations'].sum():.1%})"
                for make, reg, small in zip(
                    data["Make"],
                    data["Registrations"],
                    small_mask)
                if small]

            plt.legend(
                small_wedges,
                small_labels,
                title="Smaller Makes",
                loc="center left",
                bbox_to_anchor=(0.85, 0.5))

            plt.title(f"EV Registrations by Make for {year} for {gvwr} Vehicles", pad=30)
            plt.axis('equal')
            plt.show()

    return ev_make_market_share_df

print(ev_make_market_share("EV Sales and Market Share.xlsx"))
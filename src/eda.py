"""Exploratory Data Analysis (EDA) Module for Retail Sales Forecasting.

Generates production-grade, publication-quality visualizations and statistical
summaries to uncover trends, seasonal patterns, store performance tiers,
and holiday demand spikes. Figures are exported to reports/figures/.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def get_figures_dir() -> Path:
    """Returns and ensures the existence of the figures directory."""
    project_root = Path(__file__).resolve().parent.parent
    figures_dir = project_root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def set_plotting_style():
    """Configures high-contrast, professional matplotlib and seaborn styling."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
        "axes.edgecolor": "#cccccc",
        "axes.linewidth": 0.8,
        "grid.color": "#ebebeb",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "figure.titlesize": 14,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })


def plot_overall_sales_trend(df: pd.DataFrame, output_dir: Path) -> Path:
    """Generates time series trend of aggregated weekly sales across all stores.

    Highlights recurring annual peaks (Thanksgiving / Black Friday, Christmas, Super Bowl).
    """
    weekly_agg = df.groupby("Date").agg({
        "Weekly_Sales": "sum",
        "Holiday_Flag": "max",
    }).reset_index().sort_values("Date")

    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)
    ax.plot(
        weekly_agg["Date"],
        weekly_agg["Weekly_Sales"] / 1e6,
        color="#1f77b4",
        linewidth=2.2,
        label="Total Weekly Sales (All 45 Stores)",
    )

    # Highlight holiday weeks with red scatter markers
    holiday_weeks = weekly_agg[weekly_agg["Holiday_Flag"] == 1]
    ax.scatter(
        holiday_weeks["Date"],
        holiday_weeks["Weekly_Sales"] / 1e6,
        color="#d9534f",
        s=60,
        zorder=5,
        label="Designated Holiday Week",
    )

    # Annotate Thanksgiving/Black Friday and Christmas peak weeks
    top_weeks = weekly_agg.nlargest(3, "Weekly_Sales")
    for _, row in top_weeks.iterrows():
        date_str = row["Date"].strftime("%b %d, %Y")
        sales_val = row["Weekly_Sales"] / 1e6
        ax.annotate(
            f"Peak: {date_str}\n${sales_val:.1f}M",
            xy=(row["Date"], sales_val),
            xytext=(0, 25),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color="#990000",
            arrowprops=dict(arrowstyle="->", color="#990000", lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", fc="#fff2f2", ec="#d9534f", lw=0.8),
        )

    ax.set_title("Aggregated Retail Weekly Sales Trend & Seasonal Holiday Spikes (2010 - 2012)", pad=15)
    ax.set_xlabel("Date (Weekly Intervals)")
    ax.set_ylabel("Total Weekly Revenue ($ Millions USD)")
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    save_path = output_dir / "01_total_sales_trend.png"
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_holiday_vs_regular_sales(df: pd.DataFrame, output_dir: Path) -> Path:
    """Generates boxplot and distribution comparisons of holiday vs non-holiday sales."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Create clear label column for plotting
    plot_df = df.copy()
    plot_df["Week_Type"] = plot_df["Holiday_Flag"].map({0: "Regular Week", 1: "Holiday Week"})
    plot_df["Weekly_Sales_k"] = plot_df["Weekly_Sales"] / 1e3

    palette = {"Regular Week": "#3182bd", "Holiday Week": "#e6550d"}
    sns.boxplot(
        data=plot_df,
        x="Week_Type",
        y="Weekly_Sales_k",
        hue="Week_Type",
        palette=palette,
        legend=False,
        ax=ax1,
        boxprops=dict(alpha=0.85),
    )
    ax1.set_title("Distribution of Store Weekly Sales (Boxplot)")
    ax1.set_xlabel("Week Classification")
    ax1.set_ylabel("Weekly Sales ($ Thousands USD)")

    # Mean lines and annotation
    mean_reg = df[df["Holiday_Flag"] == 0]["Weekly_Sales"].mean() / 1e3
    mean_hol = df[df["Holiday_Flag"] == 1]["Weekly_Sales"].mean() / 1e3
    uplift_pct = ((mean_hol - mean_reg) / mean_reg) * 100

    ax1.axhline(mean_reg, color="#3182bd", linestyle="--", alpha=0.8, label=f"Regular Mean: ${mean_reg:.1f}k")
    ax1.axhline(mean_hol, color="#e6550d", linestyle="--", alpha=0.8, label=f"Holiday Mean: ${mean_hol:.1f}k (+{uplift_pct:.1f}%)")
    ax1.legend(loc="upper right", fontsize=9)

    # KDE distribution plot
    sns.kdeplot(
        plot_df[plot_df["Holiday_Flag"] == 0]["Weekly_Sales_k"],
        ax=ax2,
        color="#3182bd",
        label="Regular Weeks",
        fill=True,
        alpha=0.3,
    )
    sns.kdeplot(
        plot_df[plot_df["Holiday_Flag"] == 1]["Weekly_Sales_k"],
        ax=ax2,
        color="#e6550d",
        label="Holiday Weeks",
        fill=True,
        alpha=0.3,
    )
    ax2.set_title("Density Distribution (Kernel Density Estimate)")
    ax2.set_xlabel("Weekly Sales ($ Thousands USD)")
    ax2.set_ylabel("Probability Density")
    ax2.legend(loc="upper right", fontsize=9)

    fig.suptitle("Impact of Holiday Weeks on Store Weekly Sales Revenue", fontsize=13, y=1.02)
    plt.tight_layout()

    save_path = output_dir / "02_holiday_vs_nonholiday_sales.png"
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_store_performance_tiers(df: pd.DataFrame, output_dir: Path) -> Path:
    """Ranks all 45 stores by cumulative sales to visualize performance tiers."""
    store_totals = (
        df.groupby("Store")["Weekly_Sales"]
        .sum()
        .reset_index()
        .sort_values("Weekly_Sales", ascending=False)
    )
    store_totals["Weekly_Sales_M"] = store_totals["Weekly_Sales"] / 1e6

    fig, ax = plt.subplots(figsize=(15, 6), dpi=300)
    # Color top 5, bottom 5, and middle stores differently
    colors = []
    top_5 = set(store_totals.head(5)["Store"])
    bottom_5 = set(store_totals.tail(5)["Store"])

    for s in store_totals["Store"]:
        if s in top_5:
            colors.append("#2ca02c")  # Green for top tier
        elif s in bottom_5:
            colors.append("#d62728")  # Red for bottom tier
        else:
            colors.append("#7f7f7f")  # Grey for middle tier

    bars = ax.bar(
        range(len(store_totals)),
        store_totals["Weekly_Sales_M"],
        color=colors,
        edgecolor="#333333",
        linewidth=0.5,
    )

    ax.set_xticks(range(len(store_totals)))
    ax.set_xticklabels(store_totals["Store"], rotation=90, fontsize=8)
    ax.set_title("Total Cumulative Revenue by Store (All 45 Outlets, 2010 - 2012)", pad=15)
    ax.set_xlabel("Store Identifier (Ranked from Highest to Lowest Total Revenue)")
    ax.set_ylabel("Total Revenue ($ Millions USD)")

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ca02c", label="Top 5 Tier-1 Outlets"),
        Patch(facecolor="#7f7f7f", label="Middle Tier Outlets"),
        Patch(facecolor="#d62728", label="Bottom 5 Tier-3 Outlets"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")
    plt.tight_layout()

    save_path = output_dir / "03_store_sales_distribution.png"
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: Path) -> Path:
    """Visualizes feature correlations with Weekly_Sales and exogenous variables."""
    numeric_cols = [
        "Weekly_Sales",
        "Holiday_Flag",
        "Temperature",
        "Fuel_Price",
        "CPI",
        "Unemployment",
        "Month",
        "WeekOfYear",
        "Is_PreChristmas",
    ]
    available_cols = [c for c in numeric_cols if c in df.columns]
    corr = df[available_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7.5), dpi=300)
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation Coefficient"},
        ax=ax,
    )
    ax.set_title("Feature Correlation Matrix (Sales & Environmental Factors)", pad=15)
    plt.tight_layout()

    save_path = output_dir / "04_correlation_heatmap.png"
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_monthly_seasonality(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plots monthly average sales showing the dramatic Q4 retail surge."""
    monthly_stats = df.groupby(["Month", "Year"])["Weekly_Sales"].mean().reset_index()
    monthly_stats["Weekly_Sales_k"] = monthly_stats["Weekly_Sales"] / 1e3

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    sns.lineplot(
        data=monthly_stats,
        x="Month",
        y="Weekly_Sales_k",
        hue="Year",
        marker="o",
        palette="tab10",
        linewidth=2,
        ax=ax,
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.set_title("Monthly Average Weekly Sales by Year (Demonstrating Q4 Holiday Peak)", pad=15)
    ax.set_xlabel("Calendar Month")
    ax.set_ylabel("Average Weekly Sales ($ Thousands USD)")
    ax.legend(title="Year", loc="upper left")
    plt.tight_layout()

    save_path = output_dir / "05_monthly_seasonality.png"
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def generate_eda_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates structured statistical metrics for the EDA phase."""
    mean_regular = df[df["Holiday_Flag"] == 0]["Weekly_Sales"].mean()
    mean_holiday = df[df["Holiday_Flag"] == 1]["Weekly_Sales"].mean()
    uplift = ((mean_holiday - mean_regular) / mean_regular) * 100

    store_revenue = df.groupby("Store")["Weekly_Sales"].sum().sort_values(ascending=False)
    top_5_stores = store_revenue.head(5).to_dict()
    bottom_5_stores = store_revenue.tail(5).to_dict()

    correlations_with_target = df.select_dtypes(include=[np.number]).corr()["Weekly_Sales"].drop("Weekly_Sales").to_dict()

    return {
        "mean_regular_sales": float(mean_regular),
        "mean_holiday_sales": float(mean_holiday),
        "holiday_sales_uplift_pct": float(uplift),
        "top_5_stores_by_revenue": top_5_stores,
        "bottom_5_stores_by_revenue": bottom_5_stores,
        "correlations_with_sales": correlations_with_target,
    }


def run_eda(clean_data_path: Path | str | None = None) -> Dict[str, Any]:
    """Runs the full EDA pipeline and outputs figures and metrics."""
    set_plotting_style()
    figures_dir = get_figures_dir()

    if clean_data_path is None:
        clean_data_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "clean_sales.csv"
    else:
        clean_data_path = Path(clean_data_path)

    df = pd.read_csv(clean_data_path)
    df["Date"] = pd.to_datetime(df["Date"])

    print(f"[INFO] Generating EDA visualizations into: {figures_dir}")
    fig1 = plot_overall_sales_trend(df, figures_dir)
    print(f"  - Generated: {fig1.name}")
    fig2 = plot_holiday_vs_regular_sales(df, figures_dir)
    print(f"  - Generated: {fig2.name}")
    fig3 = plot_store_performance_tiers(df, figures_dir)
    print(f"  - Generated: {fig3.name}")
    fig4 = plot_correlation_heatmap(df, figures_dir)
    print(f"  - Generated: {fig4.name}")
    fig5 = plot_monthly_seasonality(df, figures_dir)
    print(f"  - Generated: {fig5.name}")

    metrics = generate_eda_report(df)
    return metrics


if __name__ == "__main__":
    print("=" * 60)
    print("Running Retail Sales Exploratory Data Analysis")
    print("=" * 60)
    report = run_eda()
    print("\nKey Statistical Findings:")
    print(f"  - Mean Non-Holiday Weekly Sales: ${report['mean_regular_sales']:,.2f}")
    print(f"  - Mean Holiday Weekly Sales:     ${report['mean_holiday_sales']:,.2f}")
    print(f"  - Holiday Sales Demand Uplift:   +{report['holiday_sales_uplift_pct']:.2f}%")
    print("\nTop 5 Stores by Total Revenue:")
    for s, rev in report["top_5_stores_by_revenue"].items():
        print(f"    Store {s:2d}: ${rev:,.2f}")
    print("\nBottom 5 Stores by Total Revenue:")
    for s, rev in report["bottom_5_stores_by_revenue"].items():
        print(f"    Store {s:2d}: ${rev:,.2f}")

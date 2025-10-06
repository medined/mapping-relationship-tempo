import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")

with app.setup:
    from lifelines import KaplanMeierFitter
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd


@app.cell
def _():
    from config import Config
    config = Config()

    from survival_analyzer import SurvivalAnalyzer
    survival_analyzer = SurvivalAnalyzer(config)
    return (survival_analyzer,)


@app.cell
def _(survival_analyzer):
    df = survival_analyzer.read_and_transform_data()
    return (df,)


@app.cell
def _(df):
    kmf = KaplanMeierFitter()
    kmf.fit(durations=df['duration'], event_observed=df['reconnected'])

    # Plot the survival curve
    kmf.plot_survival_function()
    ax = kmf.plot_survival_function()
    ax.set_xlabel("Days until next call")
    ax.set_ylabel("Survival probability (no reconnection yet)")
    ax.set_title("All Calls - Time-to-Reconnection (Kaplan–Meier)")
    return


@app.cell
def _(df):
    def _():
        kmf = KaplanMeierFitter()
        plt.figure(figsize=(6, 4))

        for (caller, receiver), group in df.groupby(["caller", "reciever"]):
            kmf.fit(group["duration"], event_observed=group["reconnected"], label=f"{caller} → {receiver}")
            kmf.plot_survival_function()

        plt.xlabel("Days until next call")
        plt.ylabel("Survival probability")
        plt.title("Kaplan–Meier: Time-to-Reconnection per Dyad")
        plt.legend()
        plt.tight_layout()
        plt.show()

    _()
    return


if __name__ == "__main__":
    app.run()

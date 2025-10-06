import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")

with app.setup:
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
    df
    return


if __name__ == "__main__":
    app.run()

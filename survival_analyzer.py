import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

#
# SurvivalAnalyzer class for analyzing survival data from call records
# 
class SurvivalAnalyzer:

    #
    # Initializes the SurvivalAnalyzer with a configuration object
    #
    def __init__(self, config):
        self.config = config


    def read_raw_data(self):
        return pd.read_csv(self.config.csv_file, parse_dates=["timestamp"])

    # 
    # Reads the CSV file and prepares the data for survival analysis
    #
    # The next_ts column is the timestamp of the next call between the same caller and reciever.
    # The duration column is the time until the next call (in days). If there is
    # no next call, it is the time until the end of the study (censored).
    # The reconnected column is True if there was a next call (event occurred), False if censored.
    # 
    #
    def read_and_transform_data(self):
        df = self.read_raw_data()
        df = df.sort_values(["caller", "reciever", "timestamp"])
        df["next_timestamp"] = df.groupby(["caller", "reciever"])["timestamp"].shift(-1)
        # Duration until the *next* call (in days)
        dur_next = (df["next_timestamp"] - df["timestamp"]).dt.total_seconds() / 86400.0
        study_end = df["timestamp"].max()
        dur_censored = (study_end - df["timestamp"]).dt.total_seconds() / 86400.0
        df['duration'] = dur_next.fillna(dur_censored)
        df['reconnected'] = df["next_timestamp"].notna()         # True if a reconnection happened
        return df


    def build_graph(self, df: pd.DataFrame, caller_field='caller', callee_field='reciever') -> nx.DiGraph:
        # Ensure required columns exist
        required = {caller_field, callee_field}
        if not required.issubset(df.columns):
            raise ValueError(f"dataframe must contain columns: {sorted(required)}")

        # Count calls per (caller, callee)
        edge_counts = (
            df.groupby([caller_field, callee_field], as_index=False)
            .size()
            .rename(columns={"size": "weight"})
        )

        # Build directed graph
        G = nx.DiGraph()
        for _, row in edge_counts.iterrows():
            caller, reciever, w = row[caller_field], row[callee_field], int(row["weight"])
            G.add_edge(caller, reciever, weight=w)

        return G


    def draw_graph(self, G: nx.DiGraph) -> None:
        # Layout: circular keeps three nodes cleanly spaced
        pos = nx.circular_layout(G)

        # shrink distances by 25%
        scale = 0.25
        pos = {n: p * scale for n, p in pos.items()}

        fig, ax = plt.subplots(figsize=(3.5,3.5))

        nx.draw(
            G, pos, ax=ax,
            font_size=7,
            with_labels=True, 
            node_size=1000,
            node_color="#fff9c4",
            arrows=True,
            arrowstyle="->", 
            arrowsize=20
        )

        # Keep a fixed canvas so scaling actually shortens edges visually
        ax.set_aspect("equal")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.margins(0.05)      # small padding
        plt.tight_layout()
        plt.show()
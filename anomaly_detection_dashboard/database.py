from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).parent

CSV_FILE = (
    BASE_DIR
    / "data"
    / "model_outputs"
    / "hybrid_results_for_dashboard.csv"
)

DATABASE_FILE = BASE_DIR / "alerts.db"
TABLE_NAME = "hybrid_alerts"


def create_database():
    if not CSV_FILE.exists():
        print(f"Error: CSV file not found: {CSV_FILE}")
        return

    print("Loading Hybrid model results...")
    alerts = pd.read_csv(CSV_FILE)

    required_columns = {
        "record_id",
        "actual_class",
        "if_score",
        "ae_score",
        "if_ae_agreement",
        "hybrid_score",
        "default_threshold",
        "default_prediction",
        "default_status",
        "correct_prediction",
    }

    missing_columns = required_columns - set(alerts.columns)

    if missing_columns:
        print(
            "Error: Required columns are missing: "
            + ", ".join(sorted(missing_columns))
        )
        return

    with sqlite3.connect(DATABASE_FILE) as connection:
        alerts.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False,
            chunksize=1000,
        )

        connection.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_hybrid_alerts_record_id
            ON {TABLE_NAME}(record_id)
            """
        )

        connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
            idx_hybrid_alerts_status
            ON {TABLE_NAME}(default_status)
            """
        )

        connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
            idx_hybrid_alerts_agreement
            ON {TABLE_NAME}(if_ae_agreement)
            """
        )

        connection.commit()

        stored_rows = connection.execute(
            f"SELECT COUNT(*) FROM {TABLE_NAME}"
        ).fetchone()[0]

    print(f"Database created: {DATABASE_FILE}")
    print(f"Table created: {TABLE_NAME}")
    print(f"Rows stored: {stored_rows:,}")


if __name__ == "__main__":
    create_database()
import os
import sys

# Setup paths to find 'src' and 'firebase-credentials.json' relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(SRC_DIR)

# Add 'src' to the Python path to allow imports
sys.path.insert(0, SRC_DIR)

from database.managment.firebase_manager import FirebaseManager
from database.analysis.feedback_stats import generate_report

CERT_PATH = os.path.join(ROOT_DIR, "firebase-credentials.json")

def main():
    print("Fetching feedback data from Firestore...")

    if not os.path.exists(CERT_PATH):
        print(f"ERROR: Credentials file not found at {CERT_PATH}")
        sys.exit(1)

    # Initialize DB manager and fetch data
    fm = FirebaseManager(CERT_PATH)
    data = fm.get_all_feedbacks()

    # Generate Pandas report
    report = generate_report(data)

    if not report:
        print("No feedback data found in the database.")
        return

    print("\n" + "="*50)
    print("📊 FEEDBACK ANALYSIS REPORT 📊")
    print("="*50)

    print(f"\nTotal feedbacks collected: {report['total']}")
    print(f"Global Neutrality Average Rating: {report['average_rating']:.2f} / 10")

    print("\n" + "-"*40)
    print(" AVERAGE RATING BY TOPIC (Event Query)")
    print("-" * 40)
    print(report['by_topic'])

    print("\n" + "-"*40)
    print(" CRITICAL USER COMMENTS (Rating <= 5)")
    print("-" * 40)

    critical_df = report['critical_comments']
    if critical_df.empty:
        print("No critical comments registered. Great job!")
    else:
        for _, row in critical_df.iterrows():
            print(f"[{row['rating']}/10] {row['event_query']} -> {row['comment']}")

    print("\n" + "="*50)

if __name__ == "__main__":
    main()

import pandas as pd

def generate_report(data):
    """Processes raw feedback data and generates analytical statistics."""
    if not data:
        return None

    df = pd.DataFrame(data)

    # Global stats
    total_feedbacks = len(df)
    average_rating = df['rating'].mean()

    # Stats grouped by the event topic
    by_topic = df.groupby('event_query').agg(
        average_rating=('rating', 'mean'),
        count=('rating', 'count')
    ).sort_values(by='average_rating', ascending=False)

    # Filter critical comments (Rating 5 or lower with actual text)
    critical_mask = (df['rating'] <= 5) & (df['comment'].notna()) & (df['comment'] != "")
    critical_comments = df[critical_mask][['event_query', 'rating', 'comment']]

    return {
        "total": total_feedbacks,
        "average_rating": average_rating,
        "by_topic": by_topic,
        "critical_comments": critical_comments
    }

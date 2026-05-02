import requests
import pandas as pd
import time

# Headers to mimic a real browser - important, Reddit blocks raw requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_subreddit(subreddit, timefilter="year", total=500):
    """
    Scrapes top posts from a subreddit using Reddit's public JSON endpoint.
    Handles pagination using 'after' token.
    """
    posts = []
    after = None
    
    print(f"Scraping r/{subreddit}...")

    while len(posts) < total:
        # Build URL
        url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=100&t={timefilter}"
        if after:
            url += f"&after={after}"

        # Make request
        response = requests.get(url, headers=HEADERS)

        # If Reddit blocks us, stop
        if response.status_code != 200:
            print(f"Error {response.status_code} on r/{subreddit}. Stopping.")
            break

        data = response.json()
        children = data["data"]["children"]

        # No more posts
        if not children:
            break

        for child in children:
            p = child["data"]
            posts.append({
                "subreddit": subreddit,
                "title": p.get("title", ""),
                "score": p.get("score", 0),
                "upvote_ratio": p.get("upvote_ratio", 0),
                "num_comments": p.get("num_comments", 0),
                "created_utc": pd.to_datetime(p.get("created_utc", 0), unit="s"),
                "author": p.get("author", ""),
                "url": p.get("url", ""),
                "is_self": p.get("is_self", False),
                "num_crossposts": p.get("num_crossposts", 0),
                "upvotes": p.get("ups", 0),
            })

        # Pagination token for next batch
        after = data["data"].get("after")
        if not after:
            break

        # Be polite - don't hammer Reddit's servers
        time.sleep(2)

    print(f"  Collected {len(posts)} posts from r/{subreddit}")
    return posts


# --- Main ---
subreddits = ["technology", "programming", "MachineLearning"]
all_posts = []

for sub in subreddits:
    all_posts.extend(scrape_subreddit(sub, timefilter="year", total=500))
    time.sleep(3)  # Pause between subreddits

# Save to CSV
df = pd.DataFrame(all_posts)
df.to_csv("data/reddit_posts.csv", index=False)

print(f"\nDone. Total posts collected: {len(df)}")
print(df.head())
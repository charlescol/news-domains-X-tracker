![GitHub last commit](https://img.shields.io/github/last-commit/charlescol/news-domains-X-tracker)
![GitHub repo size](https://img.shields.io/github/repo-size/charlescol/news-domains-X-tracker)
![GitHub issues](https://img.shields.io/github/issues/charlescol/news-domains-X-tracker)
![GitHub license](https://img.shields.io/github/license/charlescol/news-domains-X-tracker)

# US & International News Domains Twitter Stats Tracker

## **Project Overview**

This project aims to compile a list of major **news domains** along with their associated X (formerly Twitter) accounts. The repository includes **auto-refreshing job** to fetch real-time statistics related to these X accounts, such as follower count, tweet activity, and engagement metrics. You can find the dataset in **news-domains-x.csv**.

- Top 100 accounts (sorted by followers) are updated daily.
- The other records are updated daily in batches of 300.

The current dataset contains around 1550 news domain (>10k followers) collected from multiple sources and will be continuously enriched and updated.

This project leverages **multiple free-tier** accounts of the X API to implement its refreshing strategy. Each account can retrieve data for up to 100 accounts daily, a limitation imposed by the X API.

---

## **Auto-Update Process**

The project leverages **GitHub Actions** to automatically update the statistics for tracked X accounts:

### **Workflow:**

1. **Job 1 (Real-time priority refresh):**
   - Updates the **top 100 most-followed accounts** daily.
2. **Job 2 & Job 3 & Job 4 (Incremental updates):**

   - These jobs run in parallel to process accounts in batches of 100. With 3 tokens currently available, **records are updated daily in batches of 300**.
   - The progress is tracked using a JSON file (`state/progress.json`) to ensure no accounts are skipped.

3. **Reordering and Cleaning:**

   - Once the entire list has been processed, it is re-sorted based on the number of followers.
   - Inactive or suspended accounts are removed automatically.

4. **Commit to GitHub:**
   - The updated data is committed back to the repository, ensuring the latest statistics are always available.

---

## **Current Data Sources**

The data currently used in this project has been sourced from the following repositories:

1. [ercexpo/us-news-domains](https://github.com/ercexpo/us-news-domains)
2. [palewire/news-homepages](https://github.com/palewire/news-homepages)

More sources will be added over time.

---

## **Contributing**

We welcome contributions to expand the dataset and improve automation workflows. Feel free to submit issues and pull requests.

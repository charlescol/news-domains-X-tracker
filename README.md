# US & International News Domains Twitter Stats Tracker

## **Project Overview**

This project aims to compile a list of major **news domains** along with their associated X (formerly Twitter) accounts. The repository includes auto-refreshing job to fetch real-time statistics related to these X accounts, such as follower count, tweet activity, and engagement metrics. You can find the dataset in **news-domains-x.csv**.

This project leverages the **free tier** of the X API, which imposes certain limitations, particularly allowing **only one request per day**, with each request capable of retrieving data for up to **100 accounts at a time**. Despite these constraints, we have implemented an efficient update system that ensures continuous and meaningful data collection over time.

The current dataset has been collected from multiple sources and will be continuously enriched and updated.

---

## **Auto-Update Process**

The project leverages **GitHub Actions** to automatically update the statistics for tracked X accounts despite the API's strict limitations.

### **Workflow:**
1. **Job 1 (Real-time priority refresh):**  
   - Updates the **top 100 most-followed accounts** daily.
   
2. **Job 2 & Job 3 (Incremental updates):**  
   - These jobs work in parallel to process accounts in batches of 100.
   - The progress is tracked using a JSON file (`state/progress1.json`) to ensure no accounts are skipped.

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

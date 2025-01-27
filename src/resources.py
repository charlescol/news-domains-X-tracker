import pandas as pd # type: ignore
import requests # type: ignore
import os
import json
from datetime import datetime, timezone

CSV_FILE = 'news-domains-x.csv' # News domains dataset
PROGRESS_FILE = 'state/progress.json' # Progress file
BATCH_SIZE = 100  # Max number of X accounts to fetch per request
MAX_LOGS_RETENTION = 12 # Max number of logs to keep
LOG_DIR = 'state/logs' # Logs directory

TOKEN = os.getenv("X_BEARER_TOKEN")

def saveApiResponse(response):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f'api-response_{timestamp}.json')
    
    try:
        with open(log_file, 'w') as f:
            json.dump({"timestamp": timestamp, "response": response}, f, indent=4)
        print(f"API Response saved in {log_file}")
        manage_log_retention()
        
    except Exception as e:
        print(f"Error during the saving of the API response: {e}")

def manage_log_retention():
    try:
        log_files = sorted(
            [f for f in os.listdir(LOG_DIR) if f.startswith('api-response_') and f.endswith('.json')],
            key=lambda x: os.path.getctime(os.path.join(LOG_DIR, x))
        )
        
        while len(log_files) > MAX_LOGS_RETENTION:
            oldest_file = os.path.join(LOG_DIR, log_files.pop(0))
            os.remove(oldest_file)
            print(f"Deleted old log file: {oldest_file}")
    
    except Exception as e:
        print(f"Error during log retention management: {e}")

def extractUsernames(useProgressFile=False):
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} does not exist.")
        return []

    df = pd.read_csv(CSV_FILE)

    if os.path.exists(PROGRESS_FILE) and useProgressFile:
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
    else:
        progress = {"currentIndex": 0}

    total_accounts = len(df)
    currentIndex = progress["currentIndex"]

    endIndex = currentIndex + BATCH_SIZE

    if endIndex <= total_accounts:
        # If we haven't reached the end of the file, we can just get the next batch
        usernames = df['Username'].iloc[currentIndex:endIndex].tolist()
    else:
        # If we reach the end of the file, we need to wrap around
        wrapCount = endIndex - total_accounts
        part1 = df['Username'].iloc[currentIndex:total_accounts].tolist()
        part2 = df['Username'].iloc[0:wrapCount].tolist()
        usernames = part1 + part2

    return [u.lower().strip() for u in usernames]


def fetchXStatsMocks(usernames): 
    if not os.path.exists('test/mock-api-response.json'):
        print("Error: mock-api-response.json does not exist.")
        return None
    with open('test/mock-api-response.json', 'r') as f:  
        return json.load(f)


def fetchXStats(usernames): 
    url = "https://api.x.com/2/users/by"
    querystring = {"usernames":usernames,"user.fields":"public_metrics","tweet.fields":"public_metrics"}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
        return None


def updateAccounts(apiResponse):
    if not apiResponse or 'data' not in apiResponse:
        print("No data to update.")
        return

    df = pd.read_csv(CSV_FILE)

    df['Username'] = df['Username'].apply(lambda x: str(x).lower().strip())

    for user_data in apiResponse['data']:
        username = user_data['username'].lower().strip() 
        followers = user_data['public_metrics']['followers_count']
        following = user_data['public_metrics']['following_count']
        listed = user_data['public_metrics']['listed_count']
        likes = user_data['public_metrics']['like_count']
        medias = user_data['public_metrics']['media_count']
        tweets = user_data['public_metrics']['tweet_count']
        
        mask = df['Username'] == username
        df.loc[mask, 'Followers'] = int(followers)
        df.loc[mask, 'Following'] = int(following)
        df.loc[mask, 'Tweets'] = int(tweets)
        df.loc[mask, 'Medias'] = int(medias)
        df.loc[mask, 'Likes'] = int(likes)
        df.loc[mask, 'Listed'] = int(listed)
        df.loc[mask, 'LastModifiedDate'] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    numeric_columns = ['Followers', 'Following', 'Tweets', 'Medias', 'Likes', 'Listed']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df.to_csv(CSV_FILE, index=False)
    print(f"{len(apiResponse['data'])} accounts updated")


def removeFlaggedAccounts():
    df = pd.read_csv(CSV_FILE)
    
    initial_count = len(df)
    df = df[df['isActive'] != 0]
    df.to_csv(CSV_FILE, index=False)
    
    removed_count = initial_count - len(df)
    print(f"{removed_count} flagged accounts have been removed.")
    

def flagInvalidAccounts(apiResponse):
    if not apiResponse or 'errors' not in apiResponse:
        return
    df = pd.read_csv(CSV_FILE)
    df['Username'] = df['Username'].apply(lambda x: str(x).lower().strip())
    accounts_to_flag = []

    for error in apiResponse['errors']:
        if error.get('title') == 'Not Found Error':
            account = error.get('value', '').lower().strip()
            accounts_to_flag.append(account)

    if accounts_to_flag:
        df.loc[df['Username'].isin(accounts_to_flag), 'isActive'] = 0
        df.to_csv(CSV_FILE, index=False)
        print(f"{len(accounts_to_flag)} ivalid accounts flagged.")

def sortCSVByFollowers():
    df = pd.read_csv(CSV_FILE)
    df = df.sort_values(by='Followers', ascending=False)
    df.to_csv(CSV_FILE, index=False)
    print("CSV file has been sorted by Followers in descending order.")


def updateProgress(processed_count):
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
    else:
        progress = {"currentIndex": 0}

    df = pd.read_csv(CSV_FILE)
    total_accounts = len(df)

    progress["currentIndex"] += processed_count

    if progress["currentIndex"] >= total_accounts:
        print("A cycle is completed. Removing flagged accounts and sorting by followers.")
        
        removeFlaggedAccounts()
        sortCSVByFollowers()
    
        df = pd.read_csv(CSV_FILE)
        total_accounts = len(df)
        
        if total_accounts == 0:
            progress["currentIndex"] = 0
        else:
            progress["currentIndex"] = progress["currentIndex"] % total_accounts

    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)
    print(f"Udated Progress: index sets to value {progress['currentIndex']}.")



import pandas as pd # type: ignore
import requests # type: ignore
import os
import json


CSV_FILE = 'news-domains-x.csv'
PROGRESS_FILE = 'state/progress1.json'
BATCH_SIZE = 100  # Max number of X accounts to fetch per request

TOKEN = os.getenv("X_BEARER_TOKEN")

def run(): 
    usernames = extractUsernames()
    response = fetchXStatsMocks(",".join(usernames))
    print(response)
    if response:
        saveApiResponse(response)
        updateAccounts(response)
        updateProgress(BATCH_SIZE)
    else:
        print("Error during the Response retrieval.")
    
def saveApiResponse(response):
    try:
        with open('api-response.json', 'w') as f:
            json.dump(response, f, indent=4)
        print(f"API Response saved in api-response")
    except Exception as e:
        print(f"Error during the saving of the API response: {e}")


def extractUsernames():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} does not exist.")
        return []

    df = pd.read_csv(CSV_FILE)
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
    else:
        progress = {"currentIndex": 0}

    currentIndex = progress["currentIndex"]
    return df.iloc[currentIndex:currentIndex + BATCH_SIZE]['Username'].tolist()

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

    numeric_columns = ['Followers', 'Following', 'Tweets', 'Medias', 'Likes', 'Listed']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df.to_csv(CSV_FILE, index=False)
    print(f"{len(apiResponse['data'])} accounts updated")


def removeInvalidAccounts(apiResponse):
    if not apiResponse or 'errors' not in apiResponse:
        return
    
    df = pd.read_csv(CSV_FILE)

    df['Username'] = df['Username'].apply(lambda x: str(x).lower().strip())

    accounts_to_remove = []

    for error in apiResponse['errors']:
        if error.get('title') == 'Not Found Error':
            account = error.get('value', '').lower().strip()
            accounts_to_remove.append(account)

    if accounts_to_remove:
        initial_count = len(df)
        df = df[~df['Username'].isin(accounts_to_remove)]
        df.to_csv(CSV_FILE, index=False)

        removed_count = initial_count - len(df)
        print(f"{removed_count} invalid accounts removed.")
    else:
        print("No invalid accounts found to remove.")
    



def updateProgress(processed_count):
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
    else:
        progress = {"currentIndex": 0}

    progress["currentIndex"] += processed_count

    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)
    print(f"Udated Progress: index sets to value {progress['currentIndex']}.")



if __name__ == "__main__":
    run()
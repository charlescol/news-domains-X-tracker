import os
from resources import (
    extractUsernames,
    fetchXStats,
    saveApiResponse,
    updateAccounts,
    flagInvalidAccounts
)

def run(): 
    token = os.getenv("X_BEARER_TOKEN")
    usernames = extractUsernames()
    response = fetchXStats(",".join(usernames), token)
    print(response)
    if response:
        saveApiResponse(response)
        updateAccounts(response)
        flagInvalidAccounts(response)
    else:
        raise Exception("Error during the Response retrieval.")

if __name__ == "__main__":
    run()
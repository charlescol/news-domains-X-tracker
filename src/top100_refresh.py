import os
from resources import (
    extractUsernames,
    fetchXStatsMocks,
    saveApiResponse,
    updateAccounts,
    flagInvalidAccounts
)

def run(): 
    """
    Updates the top 100 most-followed accounts daily.
    """
    token = os.getenv("X_BEARER_TOKEN")
    usernames = extractUsernames()
    response = fetchXStatsMocks(",".join(usernames), token)
    print(response)
    if response:
        saveApiResponse(response)
        updateAccounts(response)
        flagInvalidAccounts(response)
    else:
        raise Exception("Error during the Response retrieval.")

if __name__ == "__main__":
    run()
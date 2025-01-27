from resources import (
    extractUsernames,
    fetchXStats,
    saveApiResponse,
    updateAccounts,
    flagInvalidAccounts,
    updateProgress
)

def run(): 
    usernames = extractUsernames()
    response = fetchXStats(",".join(usernames))
    print(response)
    if response:
        saveApiResponse(response)
        updateAccounts(response)
        flagInvalidAccounts(response)
    else:
        print("Error during the Response retrieval.")

if __name__ == "__main__":
    run()
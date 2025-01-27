from resources import (
    extractUsernames,
    fetchXStatsMocks,
    saveApiResponse,
    updateAccounts,
    flagInvalidAccounts,
    updateProgress
)

def run(): 
    usernames = extractUsernames()
    response = fetchXStatsMocks(",".join(usernames))
    print(response)
    if response:
        saveApiResponse(response)
        updateAccounts(response)
        flagInvalidAccounts(response)
    else:
        print("Error during the Response retrieval.")

if __name__ == "__main__":
    run()
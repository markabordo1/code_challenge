# code_challenge
code challenge for divvyDOSE
## Background
This repository holds the coding challenge for divvyDOSE. It is a flask app that serves as an API that aggregates github and bitbucket user data for a commonly named user
## Setup and Running Service
Create a new virtual environment and install the requirements from the requirements.txt file <br />
`pip install -r requirements.txt`
### Running the Flask server <br />
`python -m run`
### Adding environment config 
Under `app/environment` you can config the following static variables <br />
`GITHUB_BASE_URL = "https://api.github.com/"
BITBUCKET_BASE_URL = "https://api.bitbucket.org/2.0/"
GITHUB_AUTH_ENABLED = False
GITHUB_AUTH_TOKEN = 'REDACTED'`

This will control the base urls for each SCM here and also add authentication to be managed else where and not in version control

### Sending a request
The primary end point for this service is <br />
`http://localhost:5000/api/v1/aggregate`
<br />
It accepts post requests with a username in its body <br />
curl -X POST \
  http://localhost:5000/api/v1/aggregate \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{
	"username": "pypy"
}'

### Running unittests
To run the test file use: <br />
`python -m unittest app.tests.test_repo`


## Things to improve 
Due to time constraints I have the following list of items that I would improve on if I had more capacity
* Improve github api usage using their GraphQL API instead of the REST API for efficency and better queries for data
* Add more test coverage and integration tests interacting with the endpoint
  * An example would be testing a mock server attempting to post different data, false data
* Adding a true caching layer since the requests to both Bitbucket and Github are expensive and take time due to the level of disparate data 
* Add a more robust API document for clients to use
* Add some more error handling for higher level of detail exposed to the user
* Add more convenience methods to enhance usability such as validating usernames exist or having two different usernames map for one aggregate

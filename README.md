**Everything in this repo should be open-sourceable and general to DynamoDB.
This allows for a clean separation of concerns between business-logic and
a scalable data layer.**

# Clari dynamo
A customizable service layer around Amazon's DynamoDB.
 
## Setup
`cp conf/secrets.example.py conf/secrets.py` and setup your secrets

## Features
- Deployable instantly on Heroku
- Automatic up and down scaling with dynamic-dynamodb 
- S3 option for large fields
- KMS encryption
- Custom authentication with the rest of your stack via a callback URL (TODO)
- Installs and runs dynamo local and local test (in-memory) version

## Possibilities
- Easy migration handling (row transformation function - map reduce - AWS lambda - versioning)
- Replicate to Redshift/Aurora for analytics querying
- Push for real time updates
- Immutable tables (full record history)
- Copy on write QA connections
- Much more!

## Setup
- Get anaconda python 2.7
- Java 6+ for DynamoDB local
- `pip install -r requirements.txt && cd dynamo-local && python run.py`

## Python 3
- Everything is Python3 ready except for dynamic-dynamodb which could be split
  if worker machines are on different versions of Python. 
  

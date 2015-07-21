*Still in early alpha and limited to puts and gets.*

# ClariDynamo - DynamoDB with a cherry on top 

Wrapper service providing several high level features on top of DynamoDB, S3, KMS and other Amazon services, served with CherryPy. 

## Features
- Autoscales per request and in background based on QPS via dynamic-dynamodb
- Automatic schema migrations
- Multi-tenant
- Multi-environment
- S3 fields for large objects (encrypted with KMS)
- Installs and runs dynamo local automatically
- Easy, fast test environments with in-memory DB
- Each operation tracked, timed, and logged with app-level purpose
- Timestamped `created_at` and `updated_at` for all entities
- Deploy right now on Heroku - TODO: Add Heroku button

## Setup
- Get anaconda python 2.7 http://continuum.io/downloads
- Java 6+ for DynamoDB local
- `pip install -r requirements.txt`
- `cp conf/secrets.example.py conf/secrets.py` and setup your secrets

## Migrations
- Add new with `python new_migration.py`
- Runs at server start (TODO: in background)
- Retries failed migrations on restart

## Python 3
- Everything is Python3 ready except for dynamic-dynamodb which is on a separate
  worker container
  
## TODO
* [ ] Run migrations in background
* [ ] S3 backups
* [ ] Use IAM credentials in non-dev environments instead of basic auth
* [ ] Queries, scans, and underlying paging ability.

## Possibilities
- Instant transformations - map, filter, join, split, move, etc...
- Spark accelerated migrations and transformations  
- Web UI
- Replicate to Redshift/Aurora for analytics querying
- Topic subscriptions
- Copy on write QA environment

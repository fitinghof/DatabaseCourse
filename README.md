# Startup instructions

## Step 0

Before starting anything, make sure to remove "example" from `example.env`, typically you would also change the password at this point to something more suitable but for local testing, you can leave it as-is.

## Step 1

To start the project, first make sure you have docker, then run `docker compose up -d`
This will make sure a mysql instance with the correct password is created.
You can also do this without docker but in that case you need to make sure that the password of the MySQL server is written to the .env file.
The program expects to login as root

## Step 2

Initialize the database by running `docker exec -i mysqldb mysql -uroot -p{database password here} < dump.sql` (linux, untested)
for windows do `Get-Content dump.sql -Raw | docker exec -i mysqldb mysql -u root -p{database password here}`
This will populate the database with real data and create the initial structure.

## Step 3

Run `py program.py`
This will create a website reachable at http://127.0.0.1:5000 for interacting with the database

# Notes

All initialization commands can be found in `init.sql`

Dump command:
`docker exec mysqldb sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --routines --events --triggers --set-gtid-purged=OFF test > /tmp/dump.sql'`
then
`docker cp mysqldb:/tmp/dump.sql dump.sql`
To place it correctly

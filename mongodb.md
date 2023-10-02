# Mongo setup on schaken.decrop.net

## installation 

- install mongodb-org-server_6.0.10
- install mongodb-mongosh_2.0.1

## Admin user creation

- start mongosh
- $ use admin
- $ db.createUser({ user: "admin", pwd: passwordPrompt(), roles: [ {role: 'userAdminAnyDatabase '} ] })

## allow only authorized traffic

- edit /etc/mongod.conf
- $ bindIP: 0.0.0.0
- $ security.authorization: enabled

## setup kbsb_staging database

- mongosh
- $ db.auth('admin', xxx)
- $ use kbsb_staging

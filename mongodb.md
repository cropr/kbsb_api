# Mongo setup on schaken.decrop.net

## installation 

- install mongodb-org-server_6.0.10
- install mongodb-mongosh_2.0.1

## Admin user creation

- start mongosh
- $ use admin
- $ db.createUser({ user: "admin", pwd: passwordPrompt(), roles: [ {role: 'userAdminAnyDatabase '} ] })
- password is set to xxxMONGO

## allow only authorized traffic

- edit /etc/mongod.conf
- $ bindIP: 0.0.0.0
- $ security.authorization: enabled
- sudo service mongod restart

Now mongd is protected

## creation of user ruben with full backup restore rights 

- mongosh
- db.auth('admin', xxx)
- db.createUser({
        user: 'ruben', 
        pwd: passwordPrompt(), 
        roles:[
            {role: 'readWrite', db: 'kbsbpro'},
            {role: 'readWrite', db: 'kbsbstaging'},
            {role: 'backup', db: 'admin'},
            {role: 'restore', db: 'admin'}, 
        ]
    })

Now user ruben can backup and restore any database and has full acess to kbsbprod and kbsbstaging 

## creation of user kbsb with full readWrite rights 

- db.createUser({
        user: 'kbsb', 
        pwd: passwordPrompt(), 
        roles:[
            {role: 'readWrite', db: 'kbsbpro'},
            {role: 'readWrite', db: 'kbsbstaging'},
        ]
    })
## setup kbsbstaging and kbsbprod databases

- mongosh
- $ db.auth('admin', xxx)
- use kbsbstaging 
- use kbsbprod

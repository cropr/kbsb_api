# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# these section contains the code to interact with the old mysqldb

SALT = "OLDSITE"

from .md_member import (
    LoginValidator,
    Member,
    AnonMember,
    OldUserPasswordValidator,
)
from .member import (
    anon_getclubmembers,
    anon_getmember,
    anon_belid_from_fideid,
    anon_getfidemember,
    login,
    mgmt_getmember,
    mgmt_getclubmembers,
    old_userpassword,
    validate_membertoken,
)
from .api_member import router

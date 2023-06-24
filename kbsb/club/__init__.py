# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022
import logging

logger = logging.getLogger(__name__)

logger.info("init club")

from .md_club import (
    Club,
    ClubMember,
    ClubRole,
    ClubHistory,
    ClubIn,
    ClubUpdate,
    ClubList,
    ClubItem,
    ClubAnon,
    ClubRoleNature,
    DbClub,
    Day,
    Visibility,
)

logger.info("reading club")

from .club import (
    club_locale,
    create_club,
    delete_club,
    get_club,
    get_club_idclub,
    get_clubs,
    get_csv_clubs,
    update_club,
    verify_club_access,
    set_club,
    get_anon_clubs,
)

logger.info("reading api_club")

import kbsb.club.api_club

logger.info("club fully parsed")

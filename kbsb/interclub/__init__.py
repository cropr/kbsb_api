# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# these section contains the code to read/wrtie data from the old db

from .md_interclub import (
    InterclubClub,
    InterclubClubOptional,
    InterclubClubList,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentList,
    InterclubPlayer,
    InterclubPrevious,
    InterclubSeries,
    InterclubTransfer,
    InterclubTeam,
    InterclubVenue,
    InterclubVenuesIn,
    InterclubVenues,
    InterclubVenuesList,
    DbInterclubClub,
    DbInterclubEnrollment,
    DbInterclubPrevious,
    DbInterclubSeries,
    DbInterclubVenues,
    TransferRequestValidator,
)

from .interclub import (
    csv_interclubenrollments,
    csv_interclubvenues,
    find_interclubenrollment,
    find_interclubvenues_club,
    set_interclubenrollment,
    set_interclubvenues,
    add_team_to_series,
    setup_interclubclub,
    set_interclubclub,
    get_announcements,
)

from reddevil.page.page import PageList

import kbsb.interclub.api_interclub

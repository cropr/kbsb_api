from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from kbsb.interclub.md_interclub import ICClub, ICClubIn, ICEnrollment, ICEnrollmentIn


@register_fixture
class IcClubFactory(ModelFactory[ICClub]):
    __model__ = ICClub


@register_fixture
class IcClubInFactory(ModelFactory[ICClubIn]):
    __model__ = ICClubIn

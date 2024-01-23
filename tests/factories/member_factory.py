from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from kbsb.member.md_member import Member, AnonMember


@register_fixture
class MemberFactory(ModelFactory[Member]):
    __model__ = Member


@register_fixture
class AnonMemberFactory(ModelFactory[AnonMember]):
    __model__ = AnonMember
    Member

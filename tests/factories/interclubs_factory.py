from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from kbsb.interclubs import (
    ICClubDB,
    ICClubItem,
    ICEncounter,
    ICGame,
    ICGameDetails,
    ICPlanning,
    ICPlayerUpdate,
    ICPlayerValidationError,
    ICResult,
    ICResultItem,
    ICRound,
    ICSeries,
    ICStandingsDB,
    ICTeam,
)


@register_fixture
class IcClubDbFactory(ModelFactory[ICClubDB]):
    __model__ = ICClubDB


@register_fixture
class IcClubItemFactory(ModelFactory[ICClubItem]):
    __model__ = ICClubItem


@register_fixture
class IcEncounterFactory(ModelFactory[ICEncounter]):
    __model__ = ICEncounter


@register_fixture
class IcGameFactory(ModelFactory[ICGame]):
    __model__ = ICGame


@register_fixture
class IcGameDetailsFactory(ModelFactory[ICGameDetails]):
    __model__ = ICGameDetails


@register_fixture
class IcPlanningFactory(ModelFactory[ICPlanning]):
    __model__ = ICPlanning


@register_fixture
class IcPlayerUpdateFactory(ModelFactory[ICPlayerUpdate]):
    __model__ = ICPlayerUpdate


@register_fixture
class ICPlayerValidationErrorFactory(ModelFactory[ICPlayerValidationError]):
    __model__ = ICPlayerValidationError


@register_fixture
class IcResultFactory(ModelFactory[ICResult]):
    __model__ = ICResult


@register_fixture
class IcResultItemFactory(ModelFactory[ICResultItem]):
    __model__ = ICResultItem


@register_fixture
class IcRoundFactory(ModelFactory[ICRound]):
    __model__ = ICRound


@register_fixture
class IcSeriesFactory(ModelFactory[ICSeries]):
    __model__ = ICSeries


@register_fixture
class IcStandingsDbFactory(ModelFactory[ICStandingsDB]):
    __model__ = ICStandingsDB


@register_fixture
class IcTeamFactory(ModelFactory[ICTeam]):
    __model__ = ICTeam

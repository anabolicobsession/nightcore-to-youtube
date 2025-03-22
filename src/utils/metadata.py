import logging
import sys
from dataclasses import dataclass
from typing import Self

from src import config
from src.utils.utils import ExitCode


logger = logging.getLogger(__name__)


@dataclass
class Metadata:
    discovery_year: int
    discovery_season: int
    playlist: str

    def __post_init__(self):
        if self.discovery_year not in config.METADATA_DISCOVERY_YEARS:
            allowed_range = f'{config.METADATA_DISCOVERY_YEARS[0]} - {config.METADATA_DISCOVERY_YEARS[-1]}'
            raise ValueError(f'Invalid discovery year: {self.discovery_year}. Allowed range: {allowed_range}')

        if self.discovery_season not in config.METADATA_DISCOVERY_SEASONS:
            allowed_values = ", ".join(map(str, config.METADATA_DISCOVERY_SEASONS))
            raise ValueError(f'Invalid discovery season: {self.discovery_season}. Allowed values: {allowed_values}')

        if self.playlist not in config.METADATA_PLAYLISTS:
            allowed_values = ", ".join(["'" + x + "'" for x in config.METADATA_PLAYLISTS])
            raise ValueError(f"Invalid playlist: '{self.playlist}'. Allowed values: {allowed_values}")

    @classmethod
    def from_string(cls, string: str) -> Self:
        try:
            year, season, playlist = tuple((string).split('_'))
            year, season = int(year), int(season)
            args = year, season, playlist
            return cls(*args)
        except:
            logger.error(f'Metadata string can\'t be parsed from string: \'{string}\'', exc_info=True)
            sys.exit(ExitCode.INCORRECT_USAGE)

    def represent(
            self,
            include_attribute_names=False,
            attribute_separator=', ',
            value_separator='.',
            title_string_values=False,
    ):
        if not include_attribute_names:
            return value_separator.join(
                f'{v.title() if title_string_values and isinstance(v, str) else v}'
                for _, v in vars(self).items()
            )
        else:
            return attribute_separator.join(
                f'{self._format_attribute_name(k)}{value_separator}'
                f'{v.title() if title_string_values and isinstance(v, str) else v}'
                for k, v in vars(self).items()
            )

    @staticmethod
    def _format_attribute_name(name: str):
        return name.replace('_', ' ').capitalize()

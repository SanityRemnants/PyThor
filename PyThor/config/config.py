from pathlib import Path
import yaml
from cerberus import Validator

root = Path(__file__).parents[2]
package = root / "PyThor" 
config_file = package / "config.yaml"
config_schema = package / "config_schema.yaml"


class Config:
    def __init__(self):
        self._schema = read_yaml_into_dict(config_schema)
        self.validator = Validator(self._schema)
        self._valid_sections = self._extract_valid_sections()
        self._settings = None
        self._settings = read_yaml_into_dict(config_file)
        self.validate(self._settings)

    @property
    def settings(self) -> dict:
        return self._settings

    @settings.setter
    def settings(self, new_settings: dict) -> None:
        self._settings = new_settings

    def validate(self, config_dict: dict) -> None:
        if not config_dict:
            raise ValueError("Empty settings!")
        if not self._schema:
            raise ValueError("Empty schema!")
        if not self.validator.validate(config_dict):
            raise ValueError(f"Cerberus validation Error: " f"{self.validator.errors}")

    def _extract_valid_sections(self) -> list[str]:
        if self._schema is None:
            raise ValueError("No configuration schema provided!")
        sections = []
        for section in self._schema.keys():
            sections.append(section)
        return sections

    def override(self, section: str, **kwargs) -> None:
        if not kwargs:
            return
        if section not in self._valid_sections:
            raise ValueError("Override settings in non-existing section!")

        new_settings = self._settings
        for key, value in kwargs.items():
            new_settings[section][key] = value
        self.validate(new_settings)
        self._settings = new_settings


def read_yaml_into_dict(file_name: Path) -> dict:
    with open(file_name, encoding="utf-8") as file:
        output_dict = yaml.safe_load(file)
    return output_dict

from typing import Any

import streamlit as st


def _get_default_dict_index(choices: dict, default_value: Any) -> int:
    for index, (_, val) in enumerate(choices.items()):
        if val == default_value:
            return index
    raise ValueError("Default value not found in choices")


class CvArg:
    def __init__(self, name: str, value: Any, help: str = ""):
        self.name = name
        self.value = value
        self.help = help


class CvInt(CvArg):
    def __init__(
        self,
        name: str,
        value: int,
        range: tuple = (0, 255),
        step: int = 1,
        help: str = "",
    ):
        self.step = step
        self.range = range
        super().__init__(name, value, help)

    def __str__(self):
        return f"{self.name}: {self.value}"

    def ux(self, loc):
        return loc.slider(
            self.name,
            value=self.value,
            min_value=self.range[0],
            max_value=self.range[1],
            step=self.step,
            help=self.help,
        )

    def get(self):
        return self.value


class CvBool(CvArg):
    def __init__(self, name: str, value: bool, help: str = ""):
        super().__init__(name, value, help)

    def __str__(self):
        return f"{self.name}: {self.value}"

    def ux(self, loc):
        return loc.checkbox(self.name, value=self.value, help=self.help)

    def get(self):
        return self.value


class CvTuple(CvArg):
    def __init__(
        self,
        name: str,
        value: tuple,
        range: tuple = (0, 255),
        step: int = 1,
        help: str = "",
    ):
        self.step = step
        self.range = range
        super().__init__(name, value, help)

    def __str__(self):
        return f"{self.name}: {self.value[0]} - {self.value[1]}"

    def ux(self, loc):
        return loc.slider(
            self.name,
            value=self.value[0],
            min_value=self.range[0],
            max_value=self.range[1],
            step=self.step,
            help=self.help,
        )

    def get(self):
        return (self.value, self.value)


class CvEnum(CvArg):
    def __init__(self, name: str, value: int, choices: dict, help: str = ""):
        self.choices = choices
        super().__init__(name, value, help)

    def __str__(self):
        return f"{self.name}: {self.choices[self.value]}"

    def ux(self, loc):
        return loc.selectbox(
            self.name,
            options=list(self.choices.keys()),
            index=_get_default_dict_index(self.choices, self.value),
            help=self.help,
        )

    def get(self):
        return self.choices[self.value]

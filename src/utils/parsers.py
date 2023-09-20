"""
Parsers for different kinds of discord models we're parsing out of strings,
or any other kinds of inputs we have to parse from the user.
"""
from typing import TypeVar, Generic, Union, Tuple
from enum import Enum
from dataclasses import dataclass

import discord

T = TypeVar("T")

E = TypeVar("E")


@dataclass
class Ok(Generic[T]):
    """
    Represents a successful value return.
    """

    inner: T


@dataclass
class Err(Generic[E]):
    """
    Represents an error value return.
    """

    inner: E


Result = Union[Ok[T], Err[E]]

ParseError = Enum("ParseError", ["Eof", "CantParse"])


async def parse_text_channel(
    ctx: discord.Interaction, channels: str
) -> Result[Tuple[str, discord.TextChannel], ParseError]:
    """
    Parses a text channel mention, and returns either an Ok with the remaining
    text after the mention, and the text channel, or an parser error.
    """
    assert ctx.guild
    remaining = iter(channels)
    for character in remaining:
        if character.isspace():
            continue
        if character == "<":
            break
        # really, this is an error in parsing because we ran into a different
        # character, should communicate this.
        return Err(ParseError.CantParse)
    else:
        # Everything was whitespace.
        return Err(ParseError.Eof)

    if next(remaining) != "#":
        return Err(ParseError.CantParse)

    channel_id = ""
    while character := next(remaining):
        if character == ">":
            channel = ctx.guild.get_channel(int(channel_id))
            assert isinstance(
                channel, discord.TextChannel
            ), "the fetched channel isn't a text channel..."
            return Ok(("".join(remaining), channel))

        if character.isdigit():
            channel_id += character
            continue
    # Found no end.
    return Err(ParseError.CantParse)

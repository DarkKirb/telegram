# mautrix-telegram - A Matrix-Telegram puppeting bridge
# Copyright (C) 2021 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from asyncpg import Record
from attr import dataclass

from mautrix.types import EventID, RoomID
from mautrix.util.async_db import Database

from ..types import TelegramID

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class Reaction:
    db: ClassVar[Database] = fake_db

    mxid: EventID
    mx_room: RoomID
    tg_msgid: TelegramID
    tg_space: TelegramID
    tg_sender: TelegramID
    reaction: str

    @classmethod
    def _from_row(cls, row: Record | None) -> Reaction | None:
        if row is None:
            return None
        return cls(**row)

    columns: ClassVar[str] = "mxid, mx_room, tg_msgid, tg_space, tg_sender, reaction"

    @classmethod
    async def get_by_tgid(
        cls, tg_msgid: TelegramID, tg_space: TelegramID, tg_sender: TelegramID
    ) -> Reaction | None:
        q = (
            f"SELECT {cls.columns} FROM reaction"
            " WHERE tg_msgid=$1 AND tg_space=$2 AND tg_sender=$3"
        )
        return cls._from_row(await cls.db.fetchrow(q, tg_msgid, tg_space, tg_sender))

    @classmethod
    async def delete_all(cls, mx_room: RoomID) -> None:
        await cls.db.execute("DELETE FROM reaction WHERE mx_room=$1", mx_room)

    @classmethod
    async def get_by_mxid(
        cls, mxid: EventID, mx_room: RoomID, tg_space: TelegramID
    ) -> Reaction | None:
        q = f"SELECT {cls.columns} FROM reaction WHERE mxid=$1 AND mx_room=$2 AND tg_space=$3"
        return cls._from_row(await cls.db.fetchrow(q, mxid, mx_room, tg_space))

    @property
    def _values(self):
        return self.mxid, self.mx_room, self.tg_msgid, self.tg_space, self.tg_space, self.reaction

    async def save(self) -> None:
        q = (
            "INSERT INTO reaction (mxid, mx_room, tg_msgid, tg_space, tg_sender, reaction) "
            "VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (tg_msgid, tg_space, tg_sender) "
            "DO UPDATE SET mxid=$1, mx_room=$2, reaction=$6"
        )
        await self.db.execute(q, self._values)

    async def update(self) -> None:
        q = (
            "UPDATE reaction SET mxid=$1, mx_room=$2, reaction=$6 "
            "WHERE tg_msgid=$3 AND tg_space=$4 AND tg_sender=$5"
        )
        await self.db.execute(q, self._values)

    async def delete(self) -> None:
        q = "DELETE FROM reaction WHERE tg_msgid=$1 AND tg_space=$2 AND tg_sender=$3"
        await self.db.execute(q, self.tg_msgid, self.tg_space, self.tg_sender)

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
from asyncpg import Connection

from . import upgrade_table


@upgrade_table.register(description="Add support for reactions")
async def upgrade_v3(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE reaction (
            mxid      TEXT NOT NULL,
            mx_room   TEXT NOT NULL,
            tg_msgid  BIGINT,
            tg_space  BIGINT,
            tg_sender BIGINT,
            reaction  TEXT NOT NULL,

            -- This isn't actually used for anything, it's just for the foreign key
            _edit_index BIGINT NOT NULL DEFAULT 0,

            PRIMARY KEY (tg_msgid, tg_space, tg_sender),
            UNIQUE      (mxid, mx_room, tg_space),

            FOREIGN KEY (tg_msgid, tg_space, _edit_index)
                REFERENCES message(tgid, tg_space, edit_index)
                ON DELETE CASCADE ON UPDATE CASCADE
        )"""
    )
    await conn.execute("ALTER TABLE message ALTER COLUMN mxid SET NOT NULL")
    await conn.execute("ALTER TABLE message ALTER COLUMN mx_room SET NOT NULL")

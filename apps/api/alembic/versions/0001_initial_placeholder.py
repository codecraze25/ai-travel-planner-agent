"""Initial placeholder migration (no tables yet — Phase 1 adds users/trips).

Revision ID: 0001
Revises:
Create Date: 2026-07-03

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Phase 0: schema bootstrap only. Domain tables land in Phase 1.
    pass


def downgrade() -> None:
    pass

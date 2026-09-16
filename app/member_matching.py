"""
Automatic member matching by email address -- shared by anything that
needs to resolve an external sender/customer address to a Parcella
member (currently: the FreeScout conversation bridge,
app/freescout_sync.py).
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Member, MemberEmail


async def find_members_by_email(db: AsyncSession, email: str) -> List[Member]:
    """
    Finds members whose email address on file matches the one given
    (case-insensitive). Returns a list, since the same address can
    belong to multiple members (e.g. married couples) -- in that case
    the automation deliberately makes NO decision, leaving the choice
    to the UI (analogous to the accident-insurance logic).
    """
    result = await db.execute(
        select(Member)
        .join(MemberEmail, MemberEmail.member_id == Member.id)
        .where(
            func.lower(MemberEmail.address) == email.strip().lower(),
            Member.deleted_at.is_(None),
        )
    )
    return result.scalars().all()

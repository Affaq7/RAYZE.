"""enable row level security with deny-all policies

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-28

Supabase automatically exposes every table in the `public` schema via its
auto-generated PostgREST API to anyone holding the anon or authenticated API
key -- completely independent of, and bypassing, this FastAPI app's own JWT
auth layer. FastAPI itself connects to Postgres via the role bound to
SUPABASE_DB_URL, which owns these tables and is unaffected by RLS. Without
these deny-all policies, sensitive rows (e.g. job_applications, contact
submissions) would be directly readable/writable through Supabase's own API
using just the public anon key.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ["portfolio", "reviews", "job_postings", "job_applications", "contact_submissions"]


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')
        op.execute(
            f'CREATE POLICY deny_all_anon ON "{table}" FOR ALL TO anon USING (false) WITH CHECK (false)'
        )
        op.execute(
            f'CREATE POLICY deny_all_authenticated ON "{table}" FOR ALL TO authenticated '
            "USING (false) WITH CHECK (false)"
        )


def downgrade() -> None:
    for table in TABLES:
        op.execute(f'DROP POLICY IF EXISTS deny_all_authenticated ON "{table}"')
        op.execute(f'DROP POLICY IF EXISTS deny_all_anon ON "{table}"')
        op.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')

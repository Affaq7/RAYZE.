"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Guarded, idempotent raw SQL instead of SQLAlchemy's check-then-create
    # Enum.create(): over a pooled connection (PgBouncer/Supavisor), the
    # client-side "does this type exist" check and the CREATE TYPE that
    # follows it are two separate round trips, leaving a race window where
    # Postgres reports a duplicate even though the type didn't exist a
    # moment earlier. A single DO block does the check-and-create atomically
    # in one server-side statement.
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE job_application_status AS ENUM ('new', 'reviewed', 'contacted', 'rejected', 'hired');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE contact_submission_status AS ENUM ('new', 'contacted', 'archived');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    # create_type=False: the types above already exist, and SQLAlchemy's
    # default create_type=True would otherwise try its own check-then-create
    # again when compiling CREATE TABLE, hitting the exact same race.
    job_application_status = postgresql.ENUM(
        "new", "reviewed", "contacted", "rejected", "hired",
        name="job_application_status",
        create_type=False,
    )
    contact_submission_status = postgresql.ENUM(
        "new", "contacted", "archived",
        name="contact_submission_status",
        create_type=False,
    )

    op.create_table(
        "portfolio",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False),
        sa.Column("client_name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("cover_image_url", sa.String(1000), nullable=True),
        sa.Column("gallery", postgresql.ARRAY(sa.String(1000)), server_default="{}", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_portfolio_slug", "portfolio", ["slug"])
    op.create_index("ix_portfolio_slug", "portfolio", ["slug"])
    op.create_index("ix_portfolio_is_published", "portfolio", ["is_published"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("client_name", sa.String(200), nullable=False),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="reviews_rating_range"),
    )
    op.create_index("ix_reviews_is_published", "reviews", ["is_published"])

    op.create_table(
        "job_postings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("employment_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_open", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uq_job_postings_slug", "job_postings", ["slug"])
    op.create_index("ix_job_postings_slug", "job_postings", ["slug"])
    op.create_index("ix_job_postings_is_open", "job_postings", ["is_open"])

    op.create_table(
        "job_applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("applicant_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("resume_path", sa.String(1000), nullable=True),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column(
            "job_posting_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("job_postings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            job_application_status,
            server_default="new",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_job_applications_job_posting_id", "job_applications", ["job_posting_id"])

    op.create_table(
        "contact_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_lead", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "status",
            contact_submission_status,
            server_default="new",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("contact_submissions")
    op.drop_table("job_applications")
    op.drop_index("ix_job_postings_is_open", table_name="job_postings")
    op.drop_index("ix_job_postings_slug", table_name="job_postings")
    op.drop_table("job_postings")
    op.drop_index("ix_reviews_is_published", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_portfolio_is_published", table_name="portfolio")
    op.drop_index("ix_portfolio_slug", table_name="portfolio")
    op.drop_table("portfolio")

    op.execute("DROP TYPE IF EXISTS contact_submission_status")
    op.execute("DROP TYPE IF EXISTS job_application_status")

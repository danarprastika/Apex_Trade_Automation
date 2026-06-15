"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-14 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_status", "users", ["status"])
    
    op.create_table("exchanges",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("exchange_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_exchanges_name", "exchanges", ["name"], unique=True)
    
    op.create_table("assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("symbol", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("asset_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"], unique=True)
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"])
    op.create_index("ix_assets_status", "assets", ["status"])
    
    op.create_table("market_pairs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("exchange_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("base_asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_market_pairs_exchange_id", "market_pairs", ["exchange_id"])
    op.create_index("ix_market_pairs_base_asset_id", "market_pairs", ["base_asset_id"])
    op.create_index("ix_market_pairs_quote_asset_id", "market_pairs", ["quote_asset_id"])
    op.create_index("ix_market_pairs_symbol", "market_pairs", ["symbol"])
    op.create_index("ix_market_pairs_status", "market_pairs", ["status"])
    
    op.create_table("candles",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("market_pair_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("open", sa.Numeric(), nullable=False),
        sa.Column("high", sa.Numeric(), nullable=False),
        sa.Column("low", sa.Numeric(), nullable=False),
        sa.Column("close", sa.Numeric(), nullable=False),
        sa.Column("volume", sa.Numeric(), nullable=False),
        sa.Column("open_time", sa.DateTime(), nullable=False),
        sa.Column("close_time", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_candles_market_pair_id", "candles", ["market_pair_id"])
    op.create_index("ix_candles_timeframe", "candles", ["timeframe"])
    op.create_index("ix_candles_open_time", "candles", ["open_time"])
    
    op.create_table("strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("strategy_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_strategies_code", "strategies", ["code"], unique=True)
    op.create_index("ix_strategies_strategy_type", "strategies", ["strategy_type"])
    op.create_index("ix_strategies_status", "strategies", ["status"])
    
    op.create_table("strategy_parameters",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parameter_name", sa.String(length=100), nullable=False),
        sa.Column("parameter_value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_strategy_parameters_strategy_id", "strategy_parameters", ["strategy_id"])
    
    op.create_table("signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("market_pair_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_type", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("entry_price", sa.Numeric(), nullable=True),
        sa.Column("stop_loss", sa.Numeric(), nullable=True),
        sa.Column("take_profit", sa.Numeric(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("signal_time", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
    )
    op.create_index("ix_signals_strategy_id", "signals", ["strategy_id"])
    op.create_index("ix_signals_market_pair_id", "signals", ["market_pair_id"])
    op.create_index("ix_signals_signal_time", "signals", ["signal_time"])
    op.create_index("ix_signals_status", "signals", ["status"])
    
    op.create_table("paper_trades",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("side", sa.String(length=20), nullable=False),
        sa.Column("entry_price", sa.Numeric(), nullable=False),
        sa.Column("exit_price", sa.Numeric(), nullable=True),
        sa.Column("pnl", sa.Numeric(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("opened_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_paper_trades_signal_id", "paper_trades", ["signal_id"])
    op.create_index("ix_paper_trades_user_id", "paper_trades", ["user_id"])
    op.create_index("ix_paper_trades_symbol", "paper_trades", ["symbol"])
    op.create_index("ix_paper_trades_user_symbol", "paper_trades", ["user_id", "symbol"])
    
    op.create_table("risk_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("max_daily_loss", sa.Numeric(), nullable=True),
        sa.Column("max_open_positions", sa.Numeric(), nullable=True),
        sa.Column("risk_per_trade", sa.Numeric(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_risk_settings_user_id", "risk_settings", ["user_id"], unique=True)
    
    op.create_table("ai_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("architecture", sa.String(length=100), nullable=False),
        sa.Column("target_asset", sa.String(length=30), nullable=False),
        sa.Column("accuracy_score", sa.Numeric(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_ai_models_target_asset", "ai_models", ["target_asset"])
    
    op.create_table("predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=30), nullable=False),
        sa.Column("predicted_direction", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Numeric(), nullable=False),
        sa.Column("actual_direction", sa.String(length=20), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_predictions_model_id", "predictions", ["model_id"])
    op.create_index("ix_predictions_symbol", "predictions", ["symbol"])
    op.create_index("ix_predictions_created_at", "predictions", ["created_at"])
    
    op.create_table("ai_agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_ai_agents_role", "ai_agents", ["role"])
    
    op.create_table("agent_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_type", sa.String(length=50), nullable=False),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("output_data", postgresql.JSONB(), nullable=True),
        sa.Column("confidence", sa.Numeric(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_agent_decisions_agent_id", "agent_decisions", ["agent_id"])
    
    op.create_table("final_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("ai_agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("decision_type", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Numeric(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_final_decisions_ai_agent_id", "final_decisions", ["ai_agent_id"])
    op.create_index("ix_final_decisions_symbol", "final_decisions", ["symbol"])
    
    op.create_table("audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("final_decisions")
    op.drop_table("agent_decisions")
    op.drop_table("ai_agents")
    op.drop_table("predictions")
    op.drop_table("ai_models")
    op.drop_table("risk_settings")
    op.drop_table("paper_trades")
    op.drop_table("signals")
    op.drop_table("strategy_parameters")
    op.drop_table("strategies")
    op.drop_table("candles")
    op.drop_table("market_pairs")
    op.drop_table("assets")
    op.drop_table("exchanges")
    op.drop_table("users")
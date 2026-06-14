from sqlalchemy.orm import Session

from app.database.models.backtest import BacktestRun


def create_backtest_run(
    db: Session,
    *,
    strategy_id,
    start_date,
    end_date,
    profit_factor=None,
    drawdown=None,
    win_rate=None,
    total_trades=None,
) -> BacktestRun:
    run = BacktestRun(
        strategy_id=strategy_id,
        start_date=start_date,
        end_date=end_date,
        profit_factor=profit_factor,
        drawdown=drawdown,
        win_rate=win_rate,
        total_trades=total_trades,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

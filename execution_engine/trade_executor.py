from portfolio_engine.portfolio_manager import update_cash, add_position, remove_position, log_trade, close_trade
from data_layer.data_fetcher import get_current_price

def execute_buy(symbol: str, quantity: int, stop_loss: float, target: float):
    price = get_current_price(symbol)
    if price <= 0: return False
    
    total_cost = price * quantity
    # In a real app, check if cash >= total_cost
    update_cash(-total_cost)
    add_position(symbol, quantity, price)
    trade_id = log_trade(symbol, price, quantity, stop_loss, target)
    return trade_id

def execute_sell(symbol: str, quantity: int, trade_id: int):
    price = get_current_price(symbol)
    if price <= 0: return False
    
    total_proceeds = price * quantity
    update_cash(total_proceeds)
    remove_position(symbol, quantity)
    
    # Simple win/loss logic based on entry
    # (In a real simulation, this would be more complex)
    close_trade(trade_id, price, "closed")
    return True

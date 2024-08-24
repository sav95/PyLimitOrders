from trading_framework.execution_client import ExecutionClient, ExecutionException
from trading_framework.price_listener import PriceListener

class LimitOrderAgent(PriceListener):

    def __init__(self, execution_client: ExecutionClient) -> None:
        """
        :param execution_client: Used to buy or sell products
        """
        super().__init__()
        self.execution_client = execution_client
        self.orders = []

    def add_order(self, action: str, product_id: str, quantity: int, limit: float):
        order = {
            "action": action,
            "product_id": product_id,
            "quantity": quantity,
            "limit": limit
        }
        self.orders.append(order)

    def on_price_tick(self, product_id: str, price: float):
        executable_orders = []
        
        for order in self.orders:
            if order['product_id'] == product_id:
                try:
                    if order['action'] == 'buy' and price <= order['limit']:
                        self.execution_client.buy(product_id, order['quantity'])
                        executable_orders.append(order)
                        print(f"Executed order: Buy {order['quantity']} shares of {product_id} at ${price}")
                    elif order['action'] == 'sell' and price >= order['limit']:
                        self.execution_client.sell(product_id, order['quantity'])
                        executable_orders.append(order)
                        print(f"Executed order: Sell {order['quantity']} shares of {product_id} at ${price}")
                except ExecutionException as e:
                    print(f"Failed to execute order for {product_id} at ${price}: {str(e)}")

        # Remove executed orders
        for order in executable_orders:
            self.orders.remove(order)

if __name__ == "__main__":
    execution_client = ExecutionClient()
    agent = LimitOrderAgent(execution_client)
    
    # Buy 1000 shares of IBM if the price drops below $100
    agent.add_order("buy", "IBM", 1000, 100)
    
    # Simulate a price tick where the price of IBM drops to $99
    agent.on_price_tick("IBM", 99)

import unittest
from unittest.mock import MagicMock
from limit.limit_order_agent import LimitOrderAgent
from trading_framework.execution_client import ExecutionClient, ExecutionException

class LimitOrderAgentTest(unittest.TestCase):

    def setUp(self):
        # Create a mock ExecutionClient instance
        self.mock_execution_client = MagicMock(spec=ExecutionClient)
        
        # Create an instance of LimitOrderAgent with the mock ExecutionClient
        self.agent = LimitOrderAgent(self.mock_execution_client)

    def test_buy_order_execution(self):
        # Add a buy order for 1000 shares of IBM at a limit of $100
        self.agent.add_order("buy", "IBM", 1000, 100)

        # Simulate a price tick where IBM price drops to $99
        self.agent.on_price_tick("IBM", 99)

        # Verify that the buy method was called with the correct arguments
        self.mock_execution_client.buy.assert_called_once_with("IBM", 1000)

    def test_sell_order_execution(self):
        # Add a sell order for 500 shares of IBM at a limit of $150
        self.agent.add_order("sell", "IBM", 500, 150)

        # Simulate a price tick where IBM price rises to $151
        self.agent.on_price_tick("IBM", 151)

        # Verify that the sell method was called with the correct arguments
        self.mock_execution_client.sell.assert_called_once_with("IBM", 500)

    def test_no_execution_when_price_does_not_meet_limit(self):
        # Add a buy order for 1000 shares of IBM at a limit of $100
        self.agent.add_order("buy", "IBM", 1000, 100)

        # Simulate a price tick where IBM price is $101 (higher than the limit)
        self.agent.on_price_tick("IBM", 101)

        # Verify that the buy method was not called
        self.mock_execution_client.buy.assert_not_called()

    def test_handling_execution_exception(self):
        # Add a buy order for 1000 shares of IBM at a limit of $100
        self.agent.add_order("buy", "IBM", 1000, 100)

        # Configure the mock to raise an exception when buy is called
        self.mock_execution_client.buy.side_effect = ExecutionException("Failed to execute buy order")

        # Simulate a price tick where IBM price drops to $99
        self.agent.on_price_tick("IBM", 99)

        # Verify that the buy method was called once despite the exception
        self.mock_execution_client.buy.assert_called_once_with("IBM", 1000)

    def test_multiple_orders_execution(self):
        # Add multiple orders
        self.agent.add_order("buy", "IBM", 1000, 100)
        self.agent.add_order("sell", "AAPL", 500, 150)

        # Simulate price ticks that trigger both orders
        self.agent.on_price_tick("IBM", 99)
        self.agent.on_price_tick("AAPL", 151)

        # Verify that both buy and sell methods were called
        self.mock_execution_client.buy.assert_called_once_with("IBM", 1000)
        self.mock_execution_client.sell.assert_called_once_with("AAPL", 500)

if __name__ == '__main__':
    unittest.main()

from utils.expense_calculator import Calculator
from typing import List
from langchain.tools import tool

class CalculatorTool:
    def __init__(self):
        self.calculator = Calculator()
        self.calculator_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the calculator tool"""
        @tool
        def estimate_total_hotel_cost(price_per_night:str, total_days:float) -> float:
            """Calculate total hotel cost"""
            # Strip out spaces or common currency words if the LLM adds them
            if isinstance(price_per_night, str):
                price_per_night = "".join(c for c in price_per_night if c.isdigit() or c == '.')
            clean_price = float(price_per_night)
            clean_days = float(total_days)
            return self.calculator.multiply(clean_price, clean_days)

        @tool
        def calculate_total_expense(costs: list[float]) -> float:
            """Calculate total expense of the trip"""
            return self.calculator.calculate_total(costs) 
        
        @tool
        def calculate_daily_expense_budget(total_cost: float, days: int) -> float:
            """Calculate daily expense"""
            return self.calculator.calculate_daily_budget(total_cost, days)
        
        return [estimate_total_hotel_cost, calculate_total_expense, calculate_daily_expense_budget]
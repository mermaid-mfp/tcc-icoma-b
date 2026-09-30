from app.repositories.transaction_repository import TransactionRepository
from app.models.transaction import Transaction
from collections import defaultdict
import datetime

class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()

    def add_transaction(self, type_trans, category, amount, description, client_name, user_id):
        transaction = Transaction(
            type_trans=type_trans,
            category=category,
            amount=amount,
            description=description,
            client_name=client_name,
            user_id=user_id
        )
        return self.repo.add_transaction(transaction)

    def get_dashboard_metrics(self, user_id=None):
        transactions = self.repo.get_all_transactions(user_id=user_id)
        
        total_sales = 0.0
        total_costs = 0.0
        
        sales_by_hour = defaultdict(int)
        
        for t in transactions:
            if t.type_trans == 'sale':
                total_sales += t.amount
                # Conta a venda no horário (ex: 14h, 15h)
                if t.timestamp:
                    if isinstance(t.timestamp, datetime.datetime):
                        hour = t.timestamp.strftime("%H:00")
                        sales_by_hour[hour] += 1
            elif t.type_trans == 'cost':
                total_costs += t.amount
                
        profit_margin = 0
        if total_sales > 0:
            profit_margin = ((total_sales - total_costs) / total_sales) * 100
            
        # Determinar horário de pico
        peak_hour = "N/A"
        if sales_by_hour:
            peak_hour = max(sales_by_hour, key=sales_by_hour.get)
            
        return {
            "total_sales": total_sales,
            "total_costs": total_costs,
            "profit_margin": round(profit_margin, 2),
            "peak_hour": peak_hour,
            "recent_transactions": [t.to_dict() for t in transactions[:10]] # últimas 10 transações
        }

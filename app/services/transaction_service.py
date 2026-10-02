import datetime
import math
from collections import defaultdict

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.models.transaction import Transaction

# Horário de Brasília (o Brasil não usa mais horário de verão)
BRT = datetime.timezone(datetime.timedelta(hours=-3))

PAYMENT_LABELS = {
    "pix": "Pix",
    "dinheiro": "Dinheiro",
    "debito": "Débito",
    "credito": "Crédito",
}
PAYMENT_COLORS = {
    "pix": "#00e676",
    "dinheiro": "#ffb74d",
    "debito": "#4fc3f7",
    "credito": "#b39ddb",
}
UNKNOWN_PAYMENT_LABEL = "Não informado"
UNKNOWN_PAYMENT_COLOR = "#78909c"

WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]  # date.weekday(): segunda = 0

# Área do gráfico de linha (viewBox 330 x 130)
CHART_WIDTH = 330
CHART_HEIGHT = 130
CHART_TOP = 15      # altura da linha do valor máximo
CHART_BASE = 122    # altura do valor zero


def format_brl(value):
    """1234.5 -> 'R$ 1.234,50'"""
    text = f"{abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {text}"


def _local(timestamp):
    """Converte o horário salvo no Firestore para o horário de Brasília."""
    if not isinstance(timestamp, datetime.datetime):
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
    return timestamp.astimezone(BRT)


def _nice_max(value):
    """Arredonda para cima para um valor 'redondo' (1, 2 ou 5 vezes uma potência de 10)."""
    if value <= 0:
        return 100.0
    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 5, 10):
        if value <= step * magnitude:
            return float(step * magnitude)
    return float(10 * magnitude)


def _trend(today_value, yesterday_value, higher_is_good):
    if round(today_value - yesterday_value, 2) == 0:
        return {"icon": "bi-dash-lg", "tone": "neutral", "text": "Igual a ontem"}
    went_up = today_value > yesterday_value
    return {
        "icon": "bi-graph-up-arrow" if went_up else "bi-graph-down-arrow",
        "tone": "good" if went_up == higher_is_good else "bad",
        "text": "Acima de ontem" if went_up else "Abaixo de ontem",
    }


class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.user_repo = UserRepository()

    def add_transaction(self, type_trans, category, amount, description, client_name, user_id, payment_method=""):
        if type_trans not in ("sale", "cost"):
            raise ValueError("Escolha se é uma venda ou uma despesa.")
        if amount <= 0:
            raise ValueError("Informe um valor maior que zero.")
        if type_trans == "sale" and payment_method not in PAYMENT_LABELS:
            raise ValueError("Escolha a forma de pagamento.")
        if type_trans == "cost":
            payment_method = ""

        transaction = Transaction(
            type_trans=type_trans,
            category=category,
            amount=amount,
            description=description,
            client_name=client_name,
            user_id=user_id,
            payment_method=payment_method
        )
        return self.repo.add_transaction(transaction)

    def get_dashboard_data(self, user_id, fallback_name=""):
        transactions = self.repo.get_all_transactions(user_id=user_id)

        today = datetime.datetime.now(BRT).date()
        days = [today - datetime.timedelta(days=6 - i) for i in range(7)]

        sales_by_day = defaultdict(float)
        costs_by_day = defaultdict(float)
        sales_by_payment = defaultdict(float)

        for t in transactions:
            local = _local(t.timestamp)
            if local is None:
                continue
            day = local.date()
            if t.type_trans == "sale":
                sales_by_day[day] += t.amount
                if day in days:
                    sales_by_payment[t.payment_method or ""] += t.amount
            elif t.type_trans == "cost":
                costs_by_day[day] += t.amount

        yesterday = today - datetime.timedelta(days=1)
        sales_today = sales_by_day[today]
        costs_today = costs_by_day[today]
        profit_today = sales_today - costs_today
        profit_yesterday = sales_by_day[yesterday] - costs_by_day[yesterday]

        return {
            "nome": self._first_name(user_id, fallback_name),
            "sales_today": format_brl(sales_today),
            "costs_today": format_brl(costs_today),
            "profit_today": ("− " if profit_today < 0 else "") + format_brl(profit_today),
            "sales_trend": _trend(sales_today, sales_by_day[yesterday], higher_is_good=True),
            "costs_trend": _trend(costs_today, costs_by_day[yesterday], higher_is_good=False),
            "profit_trend": _trend(profit_today, profit_yesterday, higher_is_good=True),
            "chart": self._build_chart(days, sales_by_day),
            "payments": self._build_payments(sales_by_payment),
            "recent": [self._recent_row(t) for t in transactions[:5]],
        }

    # ---------- partes do dashboard ----------

    def _first_name(self, user_id, fallback_name):
        full_name = self.user_repo.get_name(user_id) or fallback_name or ""
        parts = full_name.split()
        return parts[0] if parts else "Vendedor"

    @staticmethod
    def _build_chart(days, sales_by_day):
        values = [sales_by_day[d] for d in days]
        axis_max = _nice_max(max(values))
        column = CHART_WIDTH / len(days)

        points = []
        for i, value in enumerate(values):
            x = (i + 0.5) * column
            y = CHART_BASE - (value / axis_max) * (CHART_BASE - CHART_TOP)
            points.append((round(x, 1), round(y, 1)))

        line = " ".join(f"{x},{y}" for x, y in points)
        area = f"{points[0][0]},{CHART_HEIGHT} {line} {points[-1][0]},{CHART_HEIGHT}"
        mid_y = (CHART_TOP + CHART_BASE) / 2

        labels = [WEEKDAYS[d.weekday()] for d in days]
        labels[-1] = "Hoje"
        summary = "Vendas por dia: " + "; ".join(
            f"{label} {format_brl(value)}" for label, value in zip(labels, values)
        )

        return {
            "line": line,
            "area": area,
            "labels": labels,
            "summary": summary,
            "top_y": CHART_TOP,
            "mid_y": mid_y,
            "top_label": format_brl(axis_max),
            "mid_label": format_brl(axis_max / 2),
            "top_pct": round(CHART_TOP / CHART_HEIGHT * 100, 1),
            "mid_pct": round(mid_y / CHART_HEIGHT * 100, 1),
            "has_sales": any(v > 0 for v in values),
        }

    @staticmethod
    def _build_payments(sales_by_payment):
        total = sum(sales_by_payment.values())
        if total <= 0:
            return {"has_sales": False, "gradient": "", "segments": [], "center_label": "Sem vendas", "center_pct": ""}

        ordered = sorted(sales_by_payment.items(), key=lambda item: item[1], reverse=True)
        percents = [round(amount / total * 100) for _, amount in ordered]
        percents[0] += 100 - sum(percents)  # garante que a soma fecha em 100%

        items, stops, start = [], [], 0.0
        for (method, amount), pct in zip(ordered, percents):
            color = PAYMENT_COLORS.get(method, UNKNOWN_PAYMENT_COLOR)
            end = start + amount / total * 100
            stops.append(f"{color} {start:.2f}% {end:.2f}%")
            items.append({
                "key": method if method in PAYMENT_LABELS else "unknown",
                "label": PAYMENT_LABELS.get(method, UNKNOWN_PAYMENT_LABEL),
                "color": color,
                "pct": pct,
            })
            start = end

        return {
            "has_sales": True,
            "gradient": ", ".join(stops),
            "segments": items,
            "center_label": items[0]["label"],
            "center_pct": f"{items[0]['pct']}%",
        }

    @staticmethod
    def _recent_row(t):
        local = _local(t.timestamp)
        is_cost = t.type_trans == "cost"
        return {
            "when": local.strftime("%d/%m/%y - %Hh") if local else "—",
            "description": t.description or ("Despesa" if is_cost else "Venda"),
            "amount": ("− " if is_cost else "") + format_brl(t.amount),
            "is_cost": is_cost,
        }

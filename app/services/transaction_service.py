import datetime
import math
from collections import defaultdict

from app.formatting import BRT, MAX_VALUE, format_brl, format_money_input, to_local as _local
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.models.transaction import Transaction

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

STATUS_LABELS = {
    "concluido": "Concluído",
    "pendente": "Pendente",
}

WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]  # date.weekday(): segunda = 0

# Área do gráfico de linha (viewBox 330 x 130)
CHART_WIDTH = 330
CHART_HEIGHT = 130
CHART_TOP = 15      # altura da linha do valor máximo
CHART_BASE = 122    # altura do valor zero

LIST_LIMIT = 100    # linhas mostradas na página Transações
DESCRIPTION_LIMIT = 80


def parse_date(text):
    """'2026-10-02' -> date, ou None se vier vazio/inválido."""
    try:
        return datetime.date.fromisoformat((text or "").strip())
    except ValueError:
        return None


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


def _signed_brl(value):
    return ("− " if value < 0 else "") + format_brl(value)


def _validated(type_trans, amount, payment_method, status):
    """Confere os dados de uma transação e devolve a forma de pagamento a salvar."""
    if type_trans not in ("sale", "cost"):
        raise ValueError("Escolha se é uma venda ou uma despesa.")
    if amount <= 0:
        raise ValueError("Informe um valor maior que zero.")
    if amount > MAX_VALUE:
        raise ValueError("O valor é alto demais.")
    if status not in STATUS_LABELS:
        raise ValueError("Escolha o status: concluído ou pendente.")
    if type_trans == "sale" and payment_method not in PAYMENT_LABELS:
        raise ValueError("Escolha a forma de pagamento.")
    return payment_method if type_trans == "sale" else ""


class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.user_repo = UserRepository()

    # ---------- criar, editar e excluir ----------

    def add_transaction(self, type_trans, category, amount, description, client_name, user_id,
                        payment_method="", status="concluido"):
        payment_method = _validated(type_trans, amount, payment_method, status)

        transaction = Transaction(
            type_trans=type_trans,
            category=category,
            amount=amount,
            description=(description or "").strip()[:DESCRIPTION_LIMIT],
            client_name=client_name,
            user_id=user_id,
            payment_method=payment_method,
            status=status
        )
        return self.repo.add_transaction(transaction)

    def update_transaction(self, user_id, transaction_id, type_trans, amount, description,
                           payment_method, status):
        self._own(user_id, transaction_id)
        payment_method = _validated(type_trans, amount, payment_method, status)

        self.repo.update_transaction(transaction_id, {
            "type_trans": type_trans,
            "category": "sale" if type_trans == "sale" else "expense",
            "amount": amount,
            "description": (description or "").strip()[:DESCRIPTION_LIMIT],
            "payment_method": payment_method,
            "status": status,
        })

    def delete_transaction(self, user_id, transaction_id):
        self._own(user_id, transaction_id)
        self.repo.delete_transaction(transaction_id)

    def _own(self, user_id, transaction_id):
        """Só o dono da transação pode mexer nela."""
        transaction = self.repo.get_transaction(transaction_id)
        if transaction is None or transaction.user_id != user_id:
            raise ValueError("Transação não encontrada.")
        return transaction

    # ---------- página Transações ----------

    def list_transactions(self, user_id, date_from=None, date_to=None, query=""):
        transactions = self.repo.get_all_transactions(user_id=user_id)
        filtered_by_date = date_from is not None or date_to is not None

        in_period = []
        for t in transactions:
            local = _local(t.timestamp)
            if local is None:
                if filtered_by_date:
                    continue
            else:
                day = local.date()
                if date_from and day < date_from:
                    continue
                if date_to and day > date_to:
                    continue
            in_period.append(t)

        # Os totais valem para o período inteiro; transações pendentes ainda não contam.
        total_in = 0.0
        balance = 0.0
        for t in in_period:
            if t.status == "pendente":
                continue
            if t.type_trans == "sale":
                total_in += t.amount
                balance += t.amount
            elif t.type_trans == "cost":
                balance -= t.amount

        needle = (query or "").strip().casefold()
        rows = [self._row(t) for t in in_period]
        if needle:
            rows = [row for row in rows if needle in row["search"]]

        if round(balance, 2) > 0:
            balance_trend = {"icon": "bi-graph-up-arrow", "tone": "good", "text": "Saldo positivo"}
        elif round(balance, 2) < 0:
            balance_trend = {"icon": "bi-graph-down-arrow", "tone": "bad", "text": "Saldo negativo"}
        else:
            balance_trend = {"icon": "bi-dash-lg", "tone": "neutral", "text": "Saldo zerado"}

        return {
            "rows": rows[:LIST_LIMIT],
            "total_rows": len(rows),
            "has_more": len(rows) > LIST_LIMIT,
            "list_limit": LIST_LIMIT,
            "total_in": format_brl(total_in),
            "balance": _signed_brl(balance),
            "balance_trend": balance_trend,
        }

    # ---------- dashboard ----------

    def get_dashboard_data(self, user_id, fallback_name=""):
        transactions = self.repo.get_all_transactions(user_id=user_id)

        today = datetime.datetime.now(BRT).date()
        days = [today - datetime.timedelta(days=6 - i) for i in range(7)]

        sales_by_day = defaultdict(float)
        costs_by_day = defaultdict(float)
        sales_by_payment = defaultdict(float)

        for t in transactions:
            if t.status == "pendente":
                continue  # ainda não foi recebido ou pago
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
            "profit_today": _signed_brl(profit_today),
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

    # ---------- linhas de tabela ----------

    @staticmethod
    def _row(t):
        local = _local(t.timestamp)
        is_cost = t.type_trans == "cost"
        status = t.status if t.status in STATUS_LABELS else "concluido"
        payment_label = "" if is_cost else PAYMENT_LABELS.get(t.payment_method, "")
        description = t.description or ("Despesa" if is_cost else "Venda")
        return {
            "id": t.id,
            "type": t.type_trans,
            "is_cost": is_cost,
            "when": local.strftime("%d/%m/%y - %Hh") if local else "—",
            "when_full": local.strftime("%d/%m/%Y às %H:%M") if local else "—",
            "description": description,
            "raw_description": t.description or "",
            "amount": ("− " if is_cost else "") + format_brl(t.amount),
            "amount_input": format_money_input(t.amount),
            "payment": t.payment_method or "",
            "payment_label": payment_label or "—",
            "status": status,
            "status_label": STATUS_LABELS[status],
            "search": f"{description} {payment_label} {STATUS_LABELS[status]}".casefold(),
        }

    def _recent_row(self, t):
        row = self._row(t)
        if row["status"] == "pendente":
            row["description"] += " (pendente)"
        return row

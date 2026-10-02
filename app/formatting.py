"""Funções de apoio: dinheiro, números e horário de Brasília."""
import datetime
import math

# Horário de Brasília (o Brasil não usa mais horário de verão)
BRT = datetime.timezone(datetime.timedelta(hours=-3))

# Limite para qualquer valor digitado (evita números absurdos)
MAX_VALUE = 1_000_000_000


def format_brl(value):
    """1234.5 -> 'R$ 1.234,50'"""
    text = f"{abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {text}"


def format_money_input(value):
    """12.5 -> '12,50' (para preencher campos de formulário)"""
    return f"{value:.2f}".replace(".", ",")


def format_quantity(value):
    """3.0 -> '3' e 2.5 -> '2,5'"""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").replace(".", ",")


def parse_decimal(text):
    """Aceita '12,50', '1.234,56', 'R$ 12,50' ou '12.50'. Levanta ValueError se não for um número."""
    text = (text or "").replace("R$", "").strip()
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("número inválido")
    return value


def to_local(timestamp):
    """Converte o horário salvo no Firestore para o horário de Brasília."""
    if not isinstance(timestamp, datetime.datetime):
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
    return timestamp.astimezone(BRT)

from functools import wraps
from flask import session, redirect, url_for, g


def login_required(view):
    """Só deixa entrar quem fez login; guarda o id do usuário em g.user_id."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user")
        if not user_id:
            return redirect(url_for("auth.login"))
        g.user_id = user_id
        return view(*args, **kwargs)
    return wrapped

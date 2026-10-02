from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from app.auth_helpers import login_required
from app.services.user_service import UserService

profile_bp = Blueprint('profile', __name__)
user_service = UserService()


@profile_bp.route('/perfil')
@login_required
def profile_page():
    profile = user_service.get_profile(g.user_id, fallback_email=session.get("email", ""))
    return render_template("dashboards/profile.html", **profile)


@profile_bp.route('/perfil/nome', methods=['POST'])
@login_required
def update_name():
    try:
        user_service.update_name(g.user_id, request.form.get('nome', ''))
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('profile.profile_page'))
    except Exception as e:
        print("Erro ao salvar nome:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return redirect(url_for('profile.profile_page'))

    flash("Nome atualizado.", "success")
    return redirect(url_for('profile.profile_page'))


@profile_bp.route('/perfil/senha', methods=['POST'])
@login_required
def reset_password():
    profile = user_service.get_profile(g.user_id, fallback_email=session.get("email", ""))
    if user_service.send_password_reset(profile["email"]):
        flash(f"Enviamos um e-mail para {profile['email']} com o link para criar uma nova senha.", "success")
    else:
        flash("Não foi possível enviar o e-mail agora. Tente de novo em instantes.", "error")
    return redirect(url_for('profile.profile_page'))


@profile_bp.route('/sair', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

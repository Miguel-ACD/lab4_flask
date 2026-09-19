import os
import random
import time
from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
mail = Mail()


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="usuario")


class LoginCode(db.Model):
    __tablename__ = "login_codes"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    codigo = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(24).hex())
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://flaskuser:flaskpass@localhost:3306/lab3_flask",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "localhost")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "1025"))
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER", "laboratorio@demo.com"
    )

    db.init_app(app)
    mail.init_app(app)

    register_routes(app)
    return app


def enviar_codigo(destino, codigo):
    mensaje = Message(
        subject="Codigo de verificacion",
        recipients=[destino],
        body=f"Tu codigo para ingresar al sistema es: {codigo}",
    )
    mail.send(mensaje)


def login_requerido():
    return "admin_id" in session


def register_routes(app):
    @app.route("/")
    def index():
        if login_requerido():
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form.get("usuario", "").strip()
            password = request.form.get("password", "")
            correo_destino = request.form.get("correo", "").strip()
            admin = Admin.query.filter_by(usuario=usuario).first()

            if not correo_destino:
                flash("Debes ingresar un correo para recibir el codigo.", "error")
                return render_template("login.html")

            if not admin or not check_password_hash(admin.password_hash, password):
                flash("Usuario o contrasena incorrectos.", "error")
                return render_template("login.html")

            codigo = str(random.randint(100000, 999999))
            login_code = LoginCode(
                admin_id=admin.id,
                codigo=codigo,
                expires_at=datetime.utcnow() + timedelta(minutes=5),
            )
            db.session.add(login_code)
            db.session.commit()

            try:
                enviar_codigo(correo_destino, codigo)
                flash(f"Se envio un codigo al correo {correo_destino}.", "ok")
            except Exception:
                print(f"Codigo de verificacion para {correo_destino}: {codigo}")
                flash(
                    "No se pudo enviar correo. Para pruebas, revisa la consola del servidor.",
                    "error",
                )

            session["pending_admin_id"] = admin.id
            return redirect(url_for("verificar_codigo"))

        return render_template("login.html")

    @app.route("/verificar", methods=["GET", "POST"])
    def verificar_codigo():
        admin_id = session.get("pending_admin_id")
        if not admin_id:
            return redirect(url_for("login"))

        if request.method == "POST":
            codigo = request.form.get("codigo", "").strip()
            registro = (
                LoginCode.query.filter_by(admin_id=admin_id, codigo=codigo, usado=False)
                .order_by(LoginCode.id.desc())
                .first()
            )

            if not registro or registro.expires_at < datetime.utcnow():
                flash("Codigo invalido o vencido.", "error")
                return render_template("verificar.html")

            registro.usado = True
            db.session.commit()
            session.pop("pending_admin_id", None)
            session["admin_id"] = admin_id
            flash("Bienvenido al panel de administracion.", "ok")
            return redirect(url_for("dashboard"))

        return render_template("verificar.html")

    @app.route("/dashboard")
    def dashboard():
        if not login_requerido():
            return redirect(url_for("login"))
        usuarios = Usuario.query.order_by(Usuario.id.asc()).all()
        return render_template("dashboard.html", usuarios=usuarios)

    @app.route("/usuarios/nuevo", methods=["GET", "POST"])
    def crear_usuario():
        if not login_requerido():
            return redirect(url_for("login"))

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            rol = request.form.get("rol", "usuario")

            if not nombre or not email or rol not in ["admin", "usuario"]:
                flash("Todos los campos son obligatorios.", "error")
                return render_template("form_usuario.html", usuario=None)

            usuario = Usuario(nombre=nombre, email=email, rol=rol)
            db.session.add(usuario)
            try:
                db.session.commit()
                flash("Usuario registrado correctamente.", "ok")
                return redirect(url_for("dashboard"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar. El correo ya existe.", "error")

        return render_template("form_usuario.html", usuario=None)

    @app.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
    def editar_usuario(id):
        if not login_requerido():
            return redirect(url_for("login"))

        usuario = Usuario.query.get_or_404(id)
        if request.method == "POST":
            usuario.nombre = request.form.get("nombre", "").strip()
            usuario.email = request.form.get("email", "").strip()
            usuario.rol = request.form.get("rol", "usuario")

            if not usuario.nombre or not usuario.email or usuario.rol not in ["admin", "usuario"]:
                flash("Todos los campos son obligatorios.", "error")
                return render_template("form_usuario.html", usuario=usuario)

            try:
                db.session.commit()
                flash("Usuario actualizado.", "ok")
                return redirect(url_for("dashboard"))
            except Exception:
                db.session.rollback()
                flash("No se pudo actualizar. Revisa si el correo ya existe.", "error")

        return render_template("form_usuario.html", usuario=usuario)

    @app.route("/usuarios/<int:id>/eliminar", methods=["POST"])
    def eliminar_usuario(id):
        if not login_requerido():
            return redirect(url_for("login"))

        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado.", "ok")
        return redirect(url_for("dashboard"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Sesion cerrada.", "ok")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        for intento in range(20):
            try:
                db.create_all()
                break
            except Exception:
                if intento == 19:
                    raise
                print("Esperando conexion con la base de datos...")
                time.sleep(2)

        if not Admin.query.filter_by(usuario="admin").first():
            admin = Admin(
                usuario="admin",
                email=os.getenv("ADMIN_EMAIL", "admin@demo.com"),
                password_hash=generate_password_hash("admin123"),
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin creado: usuario admin / contrasena admin123")
    app.run(host="0.0.0.0", port=5000, debug=True)

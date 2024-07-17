from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_manager,
    login_user,
    login_required,
    logout_user,
    user_loaded_from_request,
)
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
manager = LoginManager()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

@login_manager.user_loader
def refresh(user_id):
    return User.query.get(user_id)


class Topic(db.Model):  # База данных на форум
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)


class Comment(db.Model):  # База данных на комментарии
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, unique=True, nullable=False)
    topicId = db.Column(db.String)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(225), nullable=False)


with app.app_context():
    db.create_all()




@app.route("/login", methods=["GET", "POST"])
def login_page():
    login = request.form.get("login")
    password = request.form.get("password")

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get("next")

            return redirect(next_page)
        else:
            flash("Login or password is not correct")
    else:
        flash("Please fill login and password fields")

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("hello_world"))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for("login_page") + "?next=" + request.url)

    return response


@app.route("/")
@login_required
def index():
    return render_template("avtor.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/ivent")
@login_required
def ivent():
    return render_template("ivent.html")


@app.route("/forum", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        # Создать новый ТОПИК
        user = Topic(
            title=request.form["title"],
            description=request.form["description"],
        )
        db.session.add(user)
        db.session.commit()

    topics = db.session.execute(db.select(Topic)).scalars()
    # for topic in topics:
    # print(topic.title, topic.description, topic.id)
    return render_template("forum.html", topics=topics)


@app.route("/topic/<int:id>", methods=["GET", "POST"])
@login_required
def topic(id):
    if request.method == "POST":
        # Создать новый коммент
        comment = Comment(
            text=request.form["comment"],
            topicId=id,
        )
        db.session.add(comment)
        db.session.commit()

    # Pull the topic and irs commets
    topic = db.get_or_404(Topic, id)
    comments = Comment.query.filter_by(topicId=id).all()
    print(comments)
    for comment in comments:
        print(comments)
    return render_template("topic.html", topic=topic, comments=comments)


if __name__ == "__main__":
    app.run(debug=True)

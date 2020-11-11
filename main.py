"""
author: leep
date: 2020/10/26 22:46
"""
import os
import mongoengine.fields as fields

from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mongoengine import MongoEngine
from bson import ObjectId

from todo_form import LoginForm, RegistrationForm


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = '请先登录'

def override_json_encoder(app: Flask):
    """
    为Flask-MongoEngine添加额外的JSON序列化类型支持
    Flask-MongoEngine默认为Flask添加了BaseDocument和QuerySet类型的序列化支持，
    但对于常见的ObjectId以及Datetime数据类型缺乏支持。
    """
    from bson import ObjectId
    from datetime import date

    superclass = app.json_encoder

    class _JsonEncoder(superclass):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            if isinstance(o, date):
                return o.isoformat()
            return superclass.default(self, o)

    app.json_encoder = _JsonEncoder

override_json_encoder(app)

app.config['MONGODB_SETTINGS'] = {
    'db': 'todo_odm',
    'host': '127.0.0.1',
    'port': 27017
}
db2 = MongoEngine(app)

@app.route('/index')
def index():
    """首页"""
    todos = {}
    finished = {}
    if current_user.is_authenticated:
        todo = Todos.objects(owner=current_user.id).order_by('-date')
        todos = todo.filter(status=0)
        finished = todo.filter(status=1)
    return render_template('index.html', todos=todos, finished=finished)

@app.route('/add', methods=['POST'])
@login_required
def add():
    """新增todo"""
    todo = request.get_json()['todo']
    todo = Todos(content=todo, owner=current_user.id)
    todo.save()
    return 'added'

@app.route('/finish', methods=['POST'])
def finish():
    """标记已完成todo"""
    _id = request.get_json()['_id']
    todo = Todos.objects.get(id=ObjectId(_id))
    todo.status = 1
    todo.save()
    return 'finished'


@app.route('/delete', methods=['POST'])
def delete():
    """删除todo"""
    _id = request.get_json()['_id']
    todo = Todos.objects.get(id=ObjectId(_id))
    todo.delete()
    return 'deleted'

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = User.objects(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        flash('用户名或密码错误！')
    return render_template('login.html', form=login_form)

@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('你已登出！')
    return redirect('index')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(username=register_form.username.data,
                    password=generate_password_hash(register_form.password.data))
        user.save()
        login_user(user)
        flash('注册成功！')
        return redirect('/index')
    return render_template('register.html', form=register_form)


class User(db2.Document, UserMixin):
    """mongoengine用户集合"""
    username = fields.StringField(required=True, unique=True, sparse=True)
    password = fields.StringField(required=True)
    date = fields.DateTimeField(default=datetime.now)

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    """flask-login注册user_loader函数"""
    return User.objects(id=ObjectId(user_id)).first()


class Todos(db2.Document):
    """mongoengine todo集合"""
    content = fields.StringField(required=True)
    status = fields.IntField(choices=[0, 1], default=0)
    date = fields.DateTimeField(default=datetime.now)
    owner = fields.ObjectIdField(required=True)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
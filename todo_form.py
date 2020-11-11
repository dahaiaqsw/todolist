"""
author: leep
date: 2020/10/30 22:06
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import ValidationError


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(3, 20, message='密码长度须3-20个字符')])
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 20)])
    password = PasswordField('密码',
                             validators=[DataRequired(),
                                         Length(3, 20, message='密码长度须3-20个字符'),
                                         EqualTo('pwd_confirm', message='两次密码不一致')])
    pwd_confirm = PasswordField('重复密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, name):
        from main import User
        if User.objects(username=name.data).count() != 0:
            raise ValidationError('用户名已存在！')
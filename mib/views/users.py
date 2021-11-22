from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required)
from flask_login import current_user

from typing import Text

from mib.forms import UserForm
from mib.rao.user_manager import UserManager
from mib.auth.user import User

users = Blueprint('users', __name__)


@users.route('/create_user/', methods=['GET', 'POST'])
def create_user():
    """This method allows the creation of a new user into the database

    Returns:
        Redirects the user into his profile page, once he's logged in
    """
    form = UserForm()

    if form.is_submitted():
        email = form.data['email']
        password = form.data['password']
        first_name = form.data['first_name']
        last_name = form.data['last_name']
        birthdate = form.data['birthdate']
        date = birthdate.strftime('%Y-%m-%d')
        phone = form.data['phone']
        response = UserManager.create_user(
            email,
            password,
            first_name,
            last_name,
            date,
            phone
        )

        if response.status_code == 201:
            # in this case the request is ok!
            user = response.json()
            to_login = User.build_from_json(user["user"])
            login_user(to_login)
            return redirect(url_for('home.index', id=to_login.id))
        elif response.status_code == 200:
            # user already exists
            flash('User already exists!')
            return render_template('create_user.html', form=form)
        else:
            flash('Unexpected response from users microservice!')
            return render_template('create_user.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for errorMessage in errorMessages:
                flash('The field %s is incorrect: %s' % (fieldName, errorMessage))

    return render_template('create_user.html', form=form)


@users.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """Deletes the data of the user from the database.

    Args:
        id_ (int): takes the unique id as a parameter

    Returns:
        Redirects the view to the home page
    """

    response = UserManager.delete_user(id)
    if response.status_code != 202:
        flash("Error while deleting the user")
        return redirect(url_for('auth.profile', id=id))
        
    return redirect(url_for('home.index'))

@users.route('/users', methods=['GET'])
@login_required
def users_list():
    _q = request.args.get("q", None)
    response = UserManager.get_users_list(_q)

    if response.status_code != 200:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

    user_list = response.json()['users']

    return render_template("users_list.html", list=user_list)

@users.route("/user/<int:id>", methods=["GET"])
@login_required
def user_info(id : int) -> Text:
    response = UserManager.get_user_by_id(id)

    if response == None:
        flash("User not found!")
        return redirect(url_for('home.index'))

    print(response.birthdate)
    return render_template("user_info.html", user=response, user_id=id)

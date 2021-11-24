from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required)
from flask_login import current_user

from typing import Text

from mib.forms import UserForm, EditProfileForm
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

    if form.validate_on_submit():

        form_dict = {
            k : form.data[k] for k in form.data if k not in ["csrf_token", "submit"] and form.data[k] is not None
        }
        response = UserManager.create_user(form_dict)

        if response.status_code == 201:
            # in this case the request is ok!
            user = response.json()
            to_login = User.build_from_json(user["user"])
            login_user(to_login)
            return redirect(url_for('home.index', id=to_login.id))
        elif response.status_code == 200:
            # user already exists
            flash('User already exists!')
        else:
            flash('Unexpected response from users microservice!')

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

@users.route('/content_filter', methods=['GET'])
@login_required
def set_content_filter():

    response = UserManager._content_filter(current_user.id)
    if response.status_code == 400:
        flash("Error to set content filter")
        return redirect(url_for('users.user_info', id=current_user.id))
    
    flash("Content filter value successfully changed!")
    return redirect(url_for('users.user_info', id=current_user.id))
    

@users.route('/users', methods=['GET'])
@login_required
def users_list():
    _q = request.args.get("q", None)
    users, code = UserManager.get_users_list(_q)

    if code != 200:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

    return render_template("users_list.html", list=users)

@users.route("/user/<int:id>", methods=["GET"])
@login_required
def user_info(id : int) -> Text:
    response = UserManager.get_user_by_id(id)

    if response == None:
        flash("User not found!")
        return redirect(url_for('home.index'))

    blocked, reported = UserManager.get_user_status(id)

    return render_template(
        "user_info.html", 
        user=response,
        blocked=blocked,
        reported=reported,
    )


@users.route("/profile/edit", methods=["POST", "GET"])
@login_required
def edit_user_profile() -> Text:
    
    """
    route handling editing of user info
    """
    form = EditProfileForm()

    if form.validate_on_submit():

        form_dict = {
            k : form.data[k] for k in form.data if k not in ["csrf_token", "submit"] and form.data[k] is not None
        }
        response = UserManager.update_user(form_dict, current_user.get_id())

        if response.status_code == 404:
            flash("User not found")
        elif response.status_code == 200:
            flash("Insert the correct password")
            return redirect(url_for(users.edit_user_profile))
        elif response.status_code == 201:
            flash("User modified correctly")

        return redirect(url_for("users.user_info", id=current_user.get_id()))

    response = UserManager.get_user_by_id(current_user.get_id())
    return render_template("create_user.html", form=form, user_data=response.__dict__)


@users.route("/profile", methods=["GET"])
@login_required
def user_profile() -> Text:
    
    return redirect(url_for("users.user_info", id=current_user.get_id()))

@users.route("/blacklist", methods=['GET'])
@login_required
def blacklist():
    _q = request.args.get("q", None)
    blacklist, code = UserManager.get_users_list(_q, blacklist=True)

    if code != 200:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

    return render_template("users_list.html", list=blacklist, blacklist=True)

@users.route("/blacklist/<int:id>/add", methods=['GET'])
@login_required
def add_to_blacklist(id):
    code, message = UserManager.add_to_blacklist(id)

    if code in [201, 403, 404]:
        flash(message)
        return redirect(url_for('users.blacklist'))
    else:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

@users.route("/blacklist/<int:id>/remove", methods=['GET'])
@login_required
def remove_from_blacklist(id):
    code, message = UserManager.remove_from_blacklist(id)

    if code in [202, 404]:
        flash(message)
        return redirect(url_for('users.blacklist'))
    else:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

@users.route("/report/<int:id>", methods=['GET'])
@login_required
def report_user(id):
    code, message = UserManager.report_user(id)

    if code in [200, 201, 403, 404]:
        flash(message)
        return redirect(url_for('users.user_info', id=id))
    else:
        flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))


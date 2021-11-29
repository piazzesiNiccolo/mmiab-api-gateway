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
        code, message, user = UserManager.create_user(form_dict)

        if code in [200, 201]:
            if code == 201:
                # in this case the request is ok!
                to_login = User.build_from_json(user)
                login_user(to_login)
            flash(message)
        else:
            flash('Unexpected response from users microservice!')

        return redirect(url_for('home.index'))

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
    users, propics, code = UserManager.get_users_list(id=current_user.id, query=_q)

    if code != 200:
        if code == 404:
            flash("User not found")
        elif code == 500:
            flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))

    return render_template(
        "users_list.html", 
        list=users,
        propics=propics,
    )

@users.route("/user/<int:id>", methods=["GET"])
@login_required
def user_info(id : int) -> Text:
    user, propic = UserManager.get_user_by_id(id, cache_propic=current_user.id == id)

    if user == None:
        flash("User not found!")
        return redirect(url_for('home.index'))

    blocked, reported = UserManager.get_user_status(id)

    return render_template(
        "user_info.html", 
        user=user,
        propic=propic,
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
        code, message = UserManager.update_user(form_dict, current_user.get_id())

        if code in [200, 201, 400, 404]:
            flash(message)
            if code == 200:
                return redirect(url_for('users.edit_user_profile'))
        else:
            flash("Unexpected response from users microservice!")

        return redirect(url_for("users.user_info", id=current_user.get_id()))

    user, propic = UserManager.get_user_by_id(current_user.get_id())
    return render_template(
        "create_user.html", 
        form=form, 
        user_data=user.__dict__,
        propic=propic)


@users.route("/profile", methods=["GET"])
@login_required
def user_profile() -> Text:
    
    print(current_user.pippo)
    return redirect(url_for("users.user_info", id=current_user.get_id()))

@users.route("/blacklist", methods=['GET'])
@login_required
def blacklist():
    _q = request.args.get("q", None)
    blacklist, propics, code = UserManager.get_users_list(current_user.id, _q, blacklist=True)

    if code != 200:
        if code == 404:
            flash("User not found")
        elif code == 500:
            flash("Unexpected response from users microservice!")
        return redirect(url_for('home.index'))


    return render_template(
        "users_list.html", 
        list=blacklist, 
        propics=propics,
        blacklist=True,
    )

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

    if code in [200, 404]:
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

@users.route("/notifications", methods=['GET'])
def notifications():
    code = UserManager.notifications()

    print(code)

    return redirect(url_for('users.user_profile'))




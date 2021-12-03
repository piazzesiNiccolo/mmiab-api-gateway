import flask
from flask import login_required, flash, redirect, url_for, current_user, render_template, request, current_app
from datetime import datetime

import requests
from mib.rao.message_manager import MessageManager
from mib.forms.draft import EditMessageForm

messages = flask.Blueprint("message", __name__)

@messages.route('/message/send/<int:id_message>', methods=['POST'])
@login_required
def send(id_message):
    
    code, message = MessageManager.send_message(id_message, current_user.get_id())
    
    flash(message)
    return redirect(url_for('home.index'))

@messages.route('/draft/<int:id_message>', methods=["DELETE", "PUT"])
@login_required
def draft_edit(id_message):

    if request.method == 'DELETE':

        code, message = MessageManager.delete_draft(id_message, current_user.get_id())

        flash(message)
        return redirect(url_for('home.index'))

    elif request.method == 'PUT':
        pass

@messages.route('/draft', methods=["POST", "GET"])
@login_required
def draft():
    reply_to = request.args.get("reply_to", None)
    send_to = request.args.get("send_to", None) if reply_to is None else None
    #replying_info = MessageModel.get_replying_info(reply_to)
    replying_info = MessageManager.get_message(reply_to)

    form = EditMessageForm(recipients=[{"name": "Recipient"}])
    #available_recipients = get_recipients().json["recipients"]
    for recipient_form in form.recipients:
        recipient_form.recipient.choices = available_recipients
    if request.method == "POST":
        if form.validate_on_submit():

            new_draft = Message()
            new_draft.body_message = form.body_message.data
            new_draft.date_of_send = form.date_of_send.data
            new_draft.id_sender = current_user.id
            new_draft.reply_to = reply_to
            new_draft.to_filter = ContentFilter.filter_content(new_draft.body_message)

            new_draft = {
                "body_message" : form.body_message.data,
                "date_of_send" : form.date_of_send.data,
                "id_sender" : current_user.id,
                "reply_to" : reply_to,
                "to_filter" : ContentFilter.filter_content(new_draft.body_message)
            }

            if form.image.data:
                # save the image with a unique and safe name and store the image relative
                #  path in the db
                file = form.image.data
                name = file.filename
                name = str(uuid4()) + secure_filename(name)

                path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
                new_draft.img_path = name
                file.save(path)
            #MessageModel.add_draft(new_draft)
            draft_recipients = [int(rf.recipient.data[0]) for rf in form.recipients]
            draft_recipients = UserModel.filter_available_recipients(
                current_user.id, draft_recipients
            )

            """RecipientModel.set_recipients(
                new_draft, draft_recipients, replying=replying_info is not None
            )

            return redirect("/message/list/draft")"""

    return render_template(
        "draft_bs.html",
        form=form,
        replying_info=replying_info,
        send_to=send_to,
        available_recipients=available_recipients,
    )


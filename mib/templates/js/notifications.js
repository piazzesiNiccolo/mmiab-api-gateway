
function get_message_icon() {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-chat-dots-fill" viewBox="0 0 16 16">' + 
              '<path d="M16 8c0 3.866-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.584.296-1.925.864-4.181 1.234-.2.032-.352-.176-.273-.362.354-.836.674-1.95.77-2.966C.744 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7zM5 8a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm4 0a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>' + 
           '</svg>'
}

function get_lottery_icon() {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-hypnotize" viewBox="0 0 16 16">' + 
              '<path d="m7.949 7.998.006-.003.003.009-.01-.006Zm.025-.028v-.03l.018.01-.018.02Zm0 .015.04-.022.01.006v.04l-.029.016-.021-.012v-.028Zm.049.057v-.014l-.008.01.008.004Zm-.05-.008h.006l-.006.004v-.004Z"/>' + 
              '<path fill-rule="evenodd" d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM4.965 1.69a6.972 6.972 0 0 1 3.861-.642c.722.767 1.177 1.887 1.177 3.135 0 1.656-.802 3.088-1.965 3.766 1.263.24 2.655-.815 3.406-2.742.38-.975.537-2.023.492-2.996a7.027 7.027 0 0 1 2.488 3.003c-.303 1.01-1.046 1.966-2.128 2.59-1.44.832-3.09.85-4.26.173l.008.021.012-.006-.01.01c.42 1.218 2.032 1.9 4.08 1.586a7.415 7.415 0 0 0 2.856-1.081 6.963 6.963 0 0 1-1.358 3.662c-1.03.248-2.235.084-3.322-.544-1.433-.827-2.272-2.236-2.279-3.58l-.012-.003c-.845.972-.63 2.71.666 4.327a7.415 7.415 0 0 0 2.37 1.935 6.972 6.972 0 0 1-3.86.65c-.727-.767-1.186-1.892-1.186-3.146 0-1.658.804-3.091 1.969-3.768l-.002-.007c-1.266-.25-2.666.805-3.42 2.74a7.415 7.415 0 0 0-.49 3.012 7.026 7.026 0 0 1-2.49-3.018C1.87 9.757 2.613 8.8 3.696 8.174c1.438-.83 3.084-.85 4.253-.176l.005-.006C7.538 6.77 5.924 6.085 3.872 6.4c-1.04.16-2.03.55-2.853 1.08a6.962 6.962 0 0 1 1.372-3.667l-.002.003c1.025-.243 2.224-.078 3.306.547 1.43.826 2.269 2.23 2.28 3.573L8 7.941c.837-.974.62-2.706-.673-4.319a7.415 7.415 0 0 0-2.362-1.931Z"/>' + 
            '</svg>'
}

function get_new_notification(message, icon) {
    var alert = document.createElement("div");
    alert.role = "alert";
    alert.classList.add("alert", "alert-success", "alert-dismissible");
    alert.innerHTML = '<div class="hstack">' +
            icon + 
            '<span class="mx-3" style="max-width: 90%;">' + 
                message +
            '</span>' + 
        '</div>' + 
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"> </button>'

    return alert;
}

function _pop_notifications(notifications) {

    
    /*
    var notifications= {
        'status_code': 200,
        'status': 'success',
        'data': {
            'sender_notify': [],
            'recipient_notify': [{'id_message': 1}],
            'lottery_notify': [],
        },
    }
    */
    
    console.log(notifications)
    if (notifications.status_code == 200) {
        var alert_box = document.getElementById("alert-box")
        for (n of notifications.data.sender_notify) {
            var alert = get_new_notification(n['from_recipient'] + ' has opened the message you sent!', get_message_icon())
            alert_box.appendChild(alert);
        }
        for (n of notifications.data.recipient_notify ) {
            var alert = get_new_notification('You received a new message!', get_message_icon())
            alert_box.appendChild(alert);
        }
        for (n of notifications.data.lottery_notify ) {
            var alert = get_new_notification('You won the lottery and got a whole new point!', get_lottery_icon())
            alert_box.appendChild(alert);
        }
    }
}

function get_notifications(){
  fetch('/notifications').
      then(
          function(response) {
              return response.json();
          }
      ).then(
          function(result) {
              _pop_notifications(result.notifications)
          }
      );

}

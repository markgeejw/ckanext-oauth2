from flask import Blueprint
import ckanext.oauth2.oauth2 as oauth2
import ckanext.oauth2.constants as constants
from ckanext.oauth2.plugin import _get_previous_page


oauth2_blueprint = Blueprint('oauth2', __name__)

oauth2_helper = oauth2.OAuth2Helper()

def login():
    log.debug('login')

    # Log in attemps are fired when the user is not logged in and they click
    # on the log in button

    # Get the page where the user was when the loggin attemp was fired
    # When the user is not logged in, he/she should be redirected to the dashboard when
    # the system cannot get the previous page
    came_from_url = _get_previous_page(constants.INITIAL_PAGE)

    oauth2_helper.challenge(came_from_url)

def callback():
    try:
        token = oauth2_helper.get_token()
        user_name = oauth2_helper.identify(token)
        oauth2_helper.remember(user_name)
        oauth2_helper.update_token(user_name, token)
        oauth2_helper.redirect_from_callback()
    except Exception as e:

        session.save()

        # If the callback is called with an error, we must show the message
        error_description = toolkit.request.GET.get('error_description')
        if not error_description:
            if e.message:
                error_description = e.message
            elif hasattr(e, 'description') and e.description:
                error_description = e.description
            elif hasattr(e, 'error') and e.error:
                error_description = e.error
            else:
                error_description = type(e).__name__

        toolkit.response.status_int = 302
        redirect_url = oauth2.get_came_from(toolkit.request.params.get('state'))
        redirect_url = '/' if redirect_url == constants.INITIAL_PAGE else redirect_url
        toolkit.response.location = redirect_url
        helpers.flash_error(error_description)

oauth2_blueprint.add_url_rule(u'/user/login', view_func=login)
oauth2_blueprint.add_url_rule(u'/oauth2/callback', view_func=callback)

"""
Common utilities used by the test classes
"""

import app
import json
from flask import current_app
from flask.ext.testing import TestCase
from httpretty import HTTPretty
from models import db


class MockADSWSAPI(object):
    """
    Mock of the ADSWS API
    """
    def __init__(self, api_endpoint, response_kwargs):
        """
        Constructor
        :param api_endpoint: name of the API end point
        :param user_uid: unique API user ID to be returned
        :return: no return
        """

        self.api_endpoint = api_endpoint
        self.response_kwargs = response_kwargs

        def request_callback(request, uri, headers):
            """
            :param request: HTTP request
            :param uri: URI/URL to send the request
            :param headers: header of the HTTP request
            :return:
            """

            resp_dict = {
                'api-response': 'success',
                'token': request.headers.get(
                    'Authorization', 'No Authorization header passed!'
                )
            }

            for key in self.response_kwargs:
                resp_dict[key] = self.response_kwargs[key]

            resp = json.dumps(resp_dict)
            return 200, headers, resp

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.api_endpoint,
            body=request_callback,
            content_type="application/json"
        )

    def __enter__(self):
        """
        Defines the behaviour for __enter__
        :return: no return
        """

        HTTPretty.enable()

    def __exit__(self, etype, value, traceback):
        """
        Defines the behaviour for __exit__
        :param etype: exit type
        :param value: exit value
        :param traceback: the traceback for the exit
        :return: no return
        """

        HTTPretty.reset()
        HTTPretty.disable()


class MockEmailService(MockADSWSAPI):

    """
    Very thin wrapper around MockADSWSAPI given that I may want to use the
    default class later.
    """
    def __init__(self, stub_user):

        email_endpoint = '{api}/{email}'.format(
            api=current_app.config['BIBLIB_USER_EMAIL_ADSWS_API_URL'],
            email=stub_user.email
        )

        response_kwargs = {'uid': stub_user.absolute_uid}

        super(MockEmailService, self).__init__(
            api_endpoint=email_endpoint,
            response_kwargs=response_kwargs
        )


class TestCaseDatabase(TestCase):
    """
    Base test class for when databases are being used.
    """

    def create_app(self):
        """
        Create the wsgi application

        :return: application instance
        """
        app_ = app.create_app(config_type='TEST')
        return app_

    def setUp(self):
        """
        Set up the database for use

        :return: no return
        """
        db.create_all()

    def tearDown(self):
        """
        Remove/delete the database and the relevant connections

        :return: no return
        """
        db.session.remove()
        db.drop_all()

import app
import flask_testing as ft
import flask
from unitest.mock import patch

class BaseTestCase(ft.TestCase):
    TESTING = True

    def create_app(self):
        return app.create_app(self)


class AuthenticationTest(BaseTestCase):
    """Test cases to do with authentication."""

    def test_unauthenticated_redirect(self):
        """Unauthenticated requests to all URLs are redirected to google.login"""
        for url in ["/sign-in", "/sign-out", "/"]:
            rv = self.client.get(url)
            with app.app_context():
                ft.assertRedirects(rv, flask.url_for("google.login"))


    @patch("celery_tasks.update_name_autocomplete")
    @patch("app.is_invited")
    @patch("app.google_auth_required")
    def test_uninvited_login(self, is_invited_mock, ac_mock_task):
        """Requests authenticated with Google but not on invite list should
        show banner indicating diminished functionality.

        """
        is_invited_mock.return_value = False


    @patch("celery_tasks.update_name_autocomplete")
    @patch("app.is_invited")
    def test_invited_login(self, is_invited_mock, ac_mock_task):
        """Requests authenticated with Google and email on invite list should
        not show a banner."""
        invited = ["example@gmail.com"]
        pass


class TaskTests(BaseTestCase):
    """Test cases for tasks being called."""

    def sign_in_task(self):
        """The sign in task should send a request to the google sheets API to
        append a record to the sheet.

        """
        pass

    def sign_out_task_no_sign_in(self):
        """When there is no corresponding sign out record, the sign out task
        should append a record like sign in.

        """
        pass

    def sign_out_task_existing_sign_in(self):
        """When there is a corresponding sign out record, the sign out task
        should update this."""
        pass


class SubmissionTest(BaseTestCase):
    """Tests related to form submission."""

    def test_submit_form_sign_in(self):
        """Submitting the sign in form should submit a sign in task."""
        pass

    def test_submit_form_sign_out(self):
        """Submitting a sign out form should submit a sign out task."""
        pass

    def test_clear_signature_field(self):
        """Pressing the corresponding clear button for a signature field
        should clear it.

        """
        pass


class NaivgationTests(BaseTestCase):
    """Tests related to navigating the website."""

    def test_toggle_switch(self):
        """Toggling the switch should switch to the other mode (i.e. sign in
        -> sign out and vice versa).

        """
        pass

    def test_submit_sign_in_form(self):
        """Submitting the sign in form should redirect the user to the sign in
        page."""
        pass

    def test_submit_sign_out_form(self):
        """Submitting the sign out form should redirect the usre to the sign
        out page."""
        pass

    def test_root_redirect_to_sign_in(self):
        """Going to the root page redirects to the sign in page."""
        pass

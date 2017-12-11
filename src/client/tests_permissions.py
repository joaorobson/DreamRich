from dreamrich.tests_permissions import (
    UserToClient,
    UserToEmployee,
    UserToFinancialAdviser
)
from client.factories import ActiveClientMainFactory
from dreamrich.requests import RequestTypes
from http import HTTPStatus


class ClientToItself(UserToClient):

    factory_user = ActiveClientMainFactory

    def test_client_get_itself(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_client_delete_itself(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_client_put_itself(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_client_patch_itself(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class ClientToClient(UserToClient):

    factory_user = ActiveClientMainFactory

    def setUp(self):
        self._initialize()
        self.consulted_instance = ActiveClientMainFactory()

    def test_client_get_clients_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.FORBIDDEN)

    def test_client_get_client(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.FORBIDDEN)

    def test_client_post_client(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.FORBIDDEN)

    def test_client_delete_client(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_client_put_client(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_client_patch_client(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class ClientToEmployee(UserToEmployee):

    factory_user = ActiveClientMainFactory

    def test_clients_get_employees_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.FORBIDDEN)

    def test_client_get_employee(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.FORBIDDEN)

    def test_client_post_employee(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.FORBIDDEN)

    def test_client_delete_employee(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_client_put_employee(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_client_patch_employee(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class ClientToFinancialAdviser(UserToFinancialAdviser):

    factory_user = ActiveClientMainFactory

    def test_clients_get_financial_advisers_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_client_get_financial_adviser(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_client_post_financial_adviser(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_client_delete_financial_adviser(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_client_put_financial_adviser(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_client_patch_financial_adviser(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.OK)

from http import HTTPStatus
from dr_auth.permissions_tests import (
    UserToClient,
    UserToEmployee,
    UserToFinancialAdviser,
    UserToGeneral,
    UserToItself,
    NotAuthenticatedTests,
    NotAuthenticatedToItselfTests
)
from dr_auth.utils import PermissionsTests
from dreamrich.requests import RequestTypes
from .factories import (
    EmployeeFactory,
    FinancialAdviserFactory
)


class EmployeeToItself(UserToEmployee,
                       UserToItself,
                       NotAuthenticatedToItselfTests):

    def test_employee_get_itself(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_employee_delete_itself(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_employee_put_itself(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_employee_patch_itself(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class EmployeeToEmployee(UserToEmployee,
                         PermissionsTests,
                         NotAuthenticatedTests):

    factory_user = EmployeeFactory

    def test_employee_get_employees_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.FORBIDDEN)

    def test_employee_get_employee(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.FORBIDDEN)

    def test_employee_post_employee(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.FORBIDDEN)

    def test_employee_delete_employee(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_employee_put_employee(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_employee_patch_employee(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class EmployeeToClient(UserToClient,
                       PermissionsTests,
                       NotAuthenticatedTests):

    factory_user = EmployeeFactory

    def test_employee_get_clients_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_employee_get_client(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_employee_post_client(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_employee_delete_client(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_employee_put_client(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_employee_patch_client(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class EmployeeToFinancialAdviser(UserToFinancialAdviser,
                                 PermissionsTests,
                                 NotAuthenticatedTests):

    factory_user = EmployeeFactory

    def test_employee_get_financial_advisers_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.FORBIDDEN)

    def test_employee_get_financial_adviser(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.FORBIDDEN)

    def test_employee_post_financial_adviser(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.FORBIDDEN)

    def test_employee_delete_financial_adviser(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_employee_put_financial_adviser(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_employee_patch_financial_adviser(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class EmployeeToGeneral(UserToGeneral,
                        PermissionsTests,
                        NotAuthenticatedTests):

    factory_user = EmployeeFactory

    def test_employee_get_general(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.FORBIDDEN)

    def test_employee_delete_general(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_employee_put_general(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_employee_patch_general(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)

    def test_employee_post_general(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.FORBIDDEN)


class FinanicalAdviserToItself(UserToFinancialAdviser,
                               UserToItself,
                               NotAuthenticatedToItselfTests):

    def test_financial_adviser_get_itself(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_delete_itself(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_financial_adviser_put_itself(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_financial_adviser_patch_itself(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.OK)


class FinanicalAdviserToFinanicalAdviser(UserToFinancialAdviser,
                                         PermissionsTests,
                                         NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    def test_get_financial_advisers_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_financial_adviser(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_post_financial_adviser(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_financial_adviser_delete_financial_adviser(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_financial_adviser_put_financial_adviser(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_financial_adviser_patch_financial_adviser(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.OK)


class FinancialAdviserToRelatedClient(UserToClient,
                                      PermissionsTests,
                                      NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    relationship = PermissionsTests.Relationship(
        related_names='clients',
        many=True
    )

    def test_financial_adviser_get_clients_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_client(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_delete_client(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_financial_adviser_put_client(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_financial_adviser_patch_client(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.OK)


class FinancialAdviserToClient(UserToClient,
                               PermissionsTests,
                               NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    def test_financial_adviser_get_clients_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_client(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_post_client(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_financial_adviser_delete_client(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_financial_adviser_put_client(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_financial_adviser_patch_client(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class FinancialAdviserToEmployee(UserToEmployee,
                                 PermissionsTests,
                                 NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    def test_financial_adviser_get_employees_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_employee(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_post_employee(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_financial_adviser_delete_employee(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_financial_adviser_put_employee(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def test_financial_adviser_patch_employee(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)


class FinancialAdviserToRelatedGeneral(UserToGeneral,
                                       PermissionsTests,
                                       NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    relationship = PermissionsTests.Relationship(
        related_names='clients.financial_planning',
        many=True
    )

    def test_financial_adviser_get_financial_advisers_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_financial_adviser(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_delete_financial_adviser(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.NO_CONTENT)

    def test_financial_adviser_put_financial_adviser(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.OK)

    def test_financial_adviser_patch_financial_adviser(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.OK)


class FinancialAdviserToGeneral(UserToGeneral,
                                PermissionsTests,
                                NotAuthenticatedTests):

    factory_user = FinancialAdviserFactory

    def test_financial_adviser_get_generals_list(self):
        self.user_test_request(RequestTypes.GETLIST, HTTPStatus.OK)

    def test_financial_adviser_get_general(self):
        self.user_test_request(RequestTypes.GET, HTTPStatus.OK)

    def test_financial_adviser_post_general(self):
        self.user_test_request(RequestTypes.POST, HTTPStatus.CREATED)

    def test_financial_adviser_delete_general(self):
        self.user_test_request(RequestTypes.DELETE, HTTPStatus.FORBIDDEN)

    def test_financial_adviser_put_general(self):
        self.user_test_request(RequestTypes.PUT, HTTPStatus.FORBIDDEN)

    def financial_adviser_patch_general(self):
        self.user_test_request(RequestTypes.PATCH, HTTPStatus.FORBIDDEN)

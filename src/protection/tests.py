import datetime
from django.test import TestCase
from financial_planning.factories import (
    FinancialPlanningFactory,
    RegularCostFactory
)
from patrimony.factories import ActiveFactory
from protection.factories import (
    PrivatePensionFactory,
    ProtectionManagerFactory,
    LifeInsuranceFactory,
    EmergencyReserveFactory,
)
from protection.models import (
    PrivatePension, ReserveInLack,
    LifeInsurance, EmergencyReserve,
    ActualPatrimonySuccession, IndependencePatrimonySuccession,
)
from client.factories import ActiveClientFactory
from lib.tests import test_all_create_historic


def _create_reserve_in_lack():
    financial_planning = FinancialPlanningFactory(cdi=0.1213, ipca=0.0750)
    protection_manager = ProtectionManagerFactory(
        financial_planning=financial_planning)
    reserve_in_lack = protection_manager.reserve_in_lack
    reserve_in_lack.value_0_to_24_mounth = 13000
    reserve_in_lack.value_24_to_60_mounth = 10000
    reserve_in_lack.value_60_to_120_mounth = 5000
    reserve_in_lack.value_120_to_240_mounth = 5000

    return reserve_in_lack


class EmergencyReserveTest(TestCase):

    def setUp(self):
        financial_planning = FinancialPlanningFactory()
        self.active_manager = financial_planning.patrimony.activemanager
        patrimony = financial_planning.patrimony
        self.emergency_reserve = EmergencyReserveFactory(
            mounth_of_protection=12,
            patrimony=patrimony,
            cost_manager=financial_planning.cost_manager)

        for active in self.active_manager.actives.all():
            active.delete()

        cost_manager = financial_planning.cost_manager

        for regular_cost in cost_manager.regular_costs.all():
            regular_cost.delete()

        for arrearage in patrimony.arrearages.all():
            arrearage.delete()

        regular_costs = [{'value': 500}, {'value': 1500}, {'value': 2500}]

        for regular_cost in regular_costs:
            RegularCostFactory(**regular_cost, cost_manager=cost_manager)

    def test_necessery_value(self):
        self.assertEqual(self.emergency_reserve.necessery_value, 54000)

    def test_risk_gap_on_limit(self):
        ActiveFactory(value=54000, active_manager=self.active_manager)
        self.assertEqual(self.emergency_reserve.risk_gap, 0)

    def test_risk_gap_bigger_limit(self):
        ActiveFactory(value=59000, active_manager=self.active_manager)
        self.assertEqual(self.emergency_reserve.risk_gap, 0)

    def test_risk_gap_less_limit(self):
        ActiveFactory(value=51000, active_manager=self.active_manager)
        self.assertEqual(self.emergency_reserve.risk_gap, 3000)


class ReserveInLackTest(TestCase):
    def setUp(self):
        self.reserve_in_lack = _create_reserve_in_lack()

    def test_patrimony_necessery_in_period(self):
        self.assertAlmostEqual(
            self.reserve_in_lack.patrimony_necessery_in_period(
                24, 13000), 192124.8373901789)

    def test_patrimony_necessery_total(self):
        self.assertAlmostEqual(self.reserve_in_lack.
                               patrimony_necessery_total, 595624.31498015427)


class ProtectionManagerTest(TestCase):

    def setUp(self):
        active_client = ActiveClientFactory(
            birthday=datetime.datetime(1967, 1, 1))
        financial_planning = FinancialPlanningFactory(
            cdi=0.1213, ipca=0.075, active_client=active_client)
        self.protection_manager = ProtectionManagerFactory(
            financial_planning=financial_planning)
        self.protection_manager.private_pensions.all().update(
            value=20000, annual_investment=2000)
        for life_insurance in self.protection_manager.life_insurances.all():
            life_insurance.delete()

        for private_pension in self.protection_manager.private_pensions.all():
            private_pension.delete()

        life_insurances = [
            {'value_to_pay_annual': 2000, 'has_year_end': False},
            {'value_to_pay_annual': 2000, 'has_year_end': True,
                'year_end': 2020, },
            {'value_to_pay_annual': 1000, 'has_year_end': True,
                'year_end': 2023, }]

        for life_insurance in life_insurances:
            LifeInsuranceFactory(**life_insurance,
                                 protection_manager=self.protection_manager)

        private_pensions = [
            {'annual_investment': 5000}, {'annual_investment': 3000},
            {'annual_investment': 2000}, {'annual_investment': 8000},
        ]

        for private_pension in private_pensions:
            PrivatePensionFactory(protection_manager=self.protection_manager,
                                  **private_pension)

    def test_life_insurances_flow(self):
        data = [5000.0, 5000.0, 5000.0, 5000.0, 3000.0, 3000.0, 3000.0, 2000.0,
                2000.0, 2000.0]
        self.assertEqual(self.protection_manager.life_insurances_flow(), data)

    def test_private_pensions_total(self):
        self.assertEqual(self.protection_manager.private_pensions_total(),
                         18000)

    def test_flow(self):
        data = [23000.0, 23000.0, 23000.0, 23000.0, 21000.0, 21000.0, 21000.0,
                20000.0, 20000.0, 20000.0]
        self.assertEqual(self.protection_manager.flow(), data)


class ActualPatrimonySuccessionTest(TestCase):

    def setUp(self):
        reserve_in_lack = _create_reserve_in_lack()
        protection_manager = reserve_in_lack.protection_manager

        for private_pension in protection_manager.private_pensions.all():
            private_pension.delete()

        for life_insurance in protection_manager.life_insurances.all():
            life_insurance.delete()

        private_pensions = [
            {'value': 20000, 'annual_investment': 2000},
            {'value': 4000, 'annual_investment': 200},
        ]

        for private_pension in private_pensions:
            PrivatePensionFactory(**private_pension,
                                  protection_manager=protection_manager)

        life_insurances = [
            {'value_to_pay_annual': 2000, 'value_to_recive': 500000,
                'actual': True},
            {'value_to_pay_annual': 2000, 'value_to_recive': 200000,
                'actual': False},
            {'value_to_pay_annual': 1000, 'value_to_recive': 300000,
                'actual': True}
        ]

        for life_insurance in life_insurances:
            LifeInsuranceFactory(**life_insurance,
                                 protection_manager=protection_manager)

        self.actual_patrimony_succession = protection_manager.\
            actual_patrimony_succession
        self.actual_patrimony_succession.itcmd_tax = 0.06
        self.actual_patrimony_succession.oab_tax = 0.05
        self.actual_patrimony_succession.other_taxes = 0.02
        self.protection_manager = protection_manager

    def test_private_pension_total(self):
        self.assertEqual(self.actual_patrimony_succession.
                         private_pension_total(), 24000)

    def test_dont_have_life_insurance(self):
        for life_insurance in self.protection_manager.life_insurances.all():
            life_insurance.delete()
        self.assertEqual(self.actual_patrimony_succession.
                         life_insurance_to_recive_total(), 0)

    def test_life_insurance_to_recive_total(self):
        self.assertEqual(self.actual_patrimony_succession.
                         life_insurance_to_recive_total(), 800000)

    def test_patrimony_total(self):
        self.assertAlmostEqual(self.actual_patrimony_succession.
                               patrimony_total(), 322788.03)

    def test_patrimony_necessery_to_itcmd(self):
        self.assertAlmostEqual(self.actual_patrimony_succession.
                               patrimony_necessery_to_itcmd, 19367.2818)

    def test_patrimony_necessery_to_itcmd_with_joint_account(self):
        self.actual_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(self.actual_patrimony_succession.
                               patrimony_necessery_to_itcmd, 9683.6409)

    def test_patrimony_necessery_to_oab(self):
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_necessery_to_oab,
            16139.401500000002)

    def test_patrimony_necessery_to_oab_with_joint_account(self):
        self.actual_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_necessery_to_oab,
            8069.700750000001)

    def test_patrimony_to_other_taxes(self):
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_to_other_taxes,
            6455.7606000000005)

    def test_patrimony_to_other_taxes_joint_account(self):
        self.actual_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_to_other_taxes,
            3227.8803000000003)

    def test_patrimony_total_to_sucession(self):
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_total_to_sucession,
            41962.443900000006)

    def test_patrimony_necessery_to_sucession_joint_account(self):
        self.actual_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.actual_patrimony_succession.
            patrimony_total_to_sucession,
            20981.221950000003)

    def test_patrimony_free_of_taxes(self):
        self.assertEqual(self.actual_patrimony_succession.
                         patrimony_free_of_taxes, 824000)

    def test_leftover_after_sucession(self):
        self.assertAlmostEqual(self.actual_patrimony_succession.
                               leftover_after_sucession, 782037.5561)

    def test_need_for_vialicia(self):
        self.assertAlmostEqual(self.actual_patrimony_succession.
                               need_for_vialicia, 509201.2711198457)


class IndependencePatrimonySuccessionTest(TestCase):

    def setUp(self):
        active_client = ActiveClientFactory(
            birthday=datetime.datetime(1967, 1, 1))
        financial_planning = FinancialPlanningFactory(
            active_client=active_client, ipca=0.075)
        protection_manager = ProtectionManagerFactory(
            financial_planning=financial_planning)
        reserve_in_lack = _create_reserve_in_lack()
        protection_manager = reserve_in_lack.protection_manager
        protection_manager.financial_planning = financial_planning

        for private_pension in protection_manager.private_pensions.all():
            private_pension.delete()

        for life_insurance in protection_manager.life_insurances.all():
            life_insurance.delete()

        private_pensions = [
            {'value': 20000, 'annual_investment': 2000, 'rate': 0.1213},
            {'value': 4000, 'annual_investment': 200, 'rate': 0.09},
            {'value': 4000, 'annual_investment': 200, 'rate': 0.09},
        ]

        self.private_pensions_array = []

        for private_pension in private_pensions:
            element = PrivatePensionFactory(
                **private_pension, protection_manager=protection_manager)
            self.private_pensions_array.append(element)

        life_insurances = [
            {'value_to_pay_annual': 2000, 'value_to_recive': 500000,
                'actual': True},
            {'value_to_pay_annual': 2000, 'value_to_recive': 200000,
                'actual': False},
            {'value_to_pay_annual': 1000, 'value_to_recive': 300000,
                'actual': True},
            {'value_to_pay_annual': 1000, 'value_to_recive': 300000,
                'actual': True},
        ]

        for life_insurance in life_insurances:
            LifeInsuranceFactory(**life_insurance,
                                 protection_manager=protection_manager)

        self.future_patrimony_succession =\
            protection_manager.future_patrimony_succession
        self.future_patrimony_succession.itcmd_tax = 0.06
        self.future_patrimony_succession.oab_tax = 0.05
        self.future_patrimony_succession.other_taxes = 0.02
        self.protection_manager = protection_manager

    def test_private_pension_total(self):
        self.assertAlmostEqual(self.future_patrimony_succession.
                               private_pension_total(), 68297.050164)

    def test_private_pension_individual(self):
        self.assertAlmostEqual(self.private_pensions_array[0].
                               value_moniterized(), 54847.2658609)

    def test_dont_have_life_insurance(self):
        for life_insurance in self.protection_manager.life_insurances.all():
            life_insurance.delete()
        self.assertEqual(self.future_patrimony_succession.
                         life_insurance_to_recive_total(), 0)

    def test_life_insurance_to_recive_total(self):
        self.assertEqual(self.future_patrimony_succession.
                         life_insurance_to_recive_total(), 1300000)

    def test_patrimony_total(self):
        self.assertEqual(self.future_patrimony_succession.patrimony_total(),
                         9054063.617092194)

    def test_patrimony_necessery_to_itcmd(self):
        self.assertAlmostEqual(
            self.future_patrimony_succession.patrimony_necessery_to_itcmd,
            543243.8170255317)

    def test_patrimony_necessery_to_itcmd_with_joint_account(self):
        self.future_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(self.future_patrimony_succession.
                               patrimony_necessery_to_itcmd,
                               271621.90851276583)

    def test_patrimony_necessery_to_oab(self):
        self.assertAlmostEqual(self.future_patrimony_succession.
                               patrimony_necessery_to_oab, 452703.1808546097)

    def test_patrimony_necessery_to_oab_with_joint_account(self):
        self.future_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_necessery_to_oab,
            226351.59042730485)

    def test_patrimony_to_other_taxes(self):
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_to_other_taxes,
            181081.2723418439)

    def test_patrimony_to_other_taxes_joint_account(self):
        self.future_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_to_other_taxes,
            90540.63617092195)

    def test_patrimony_total_to_sucession(self):
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_total_to_sucession,
            1177028.2702219852)

    def test_patrimony_necessery_to_sucession_joint_account(self):
        self.future_patrimony_succession.protection_manager.\
            financial_planning.active_client.bank_account.joint_account = True
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_total_to_sucession,
            588514.1351109926)

    def test_patrimony_free_of_taxes(self):
        self.assertAlmostEqual(
            self.future_patrimony_succession.
            patrimony_free_of_taxes,
            1368297.0501640132)

    def test_leftover_after_sucession(self):
        self.assertAlmostEqual(self.future_patrimony_succession.
                               leftover_after_sucession, 191268.77994202799)

    def test_need_for_vialicia(self):
        self.assertAlmostEqual(
            self.future_patrimony_succession.need_for_vialicia,
            8649708.0820540674)


class PrivatePensionTest(TestCase):

    def setUp(self):
        protection_manager = ProtectionManagerFactory()
        self.private_pension = protection_manager.private_pensions.first()

    def test_active_type_when_create(self):
        self.assertEqual(self.private_pension.active_type.name, 'PREVIDÊNCIA')

    def test_active_type_if_deleted(self):
        self.private_pension.active_type.delete()
        self.assertEqual(self.private_pension.active_type.name, 'PREVIDÊNCIA')

    def test_active_type_if_deleted_and_save(self):
        self.private_pension.active_type.delete()
        self.private_pension.active_type.save()
        self.assertEqual(self.private_pension.active_type.name, 'PREVIDÊNCIA')

    def test_active_type_if_changed_name(self):
        self.private_pension.active_type.name = 'Other name'
        self.private_pension.save()
        self.assertEqual(self.private_pension.active_type.name, 'PREVIDÊNCIA')


class HistoricalProtectionCreateTest(TestCase):

    def test_all_models(self):
        models = [ReserveInLack, LifeInsurance, PrivatePension,
                  ActualPatrimonySuccession, IndependencePatrimonySuccession]
        test_all_create_historic(self, models, ProtectionManagerFactory)

    # This method is to correct pylint error
    def emergency_reserve_case(self, model):
        financial_planning = FinancialPlanningFactory()
        patrimony = financial_planning.patrimony
        self.assertEqual(0, model.history.count())
        EmergencyReserveFactory(patrimony=patrimony,
                                cost_manager=financial_planning.cost_manager)
        self.assertEqual(1, model.history.count())

    def test_emergency_reserve(self):
        self.emergency_reserve_case(EmergencyReserve)

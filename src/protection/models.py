import datetime
import numpy
from django.db import models
from django.db.models import Sum
from financial_planning.models import FinancialPlanning


class ReserveInLack(models.Model):

    value_0_to_24_month = models.PositiveSmallIntegerField()

    value_24_to_60_month = models.PositiveSmallIntegerField()

    value_60_to_120_month = models.PositiveSmallIntegerField()

    value_120_to_240_month = models.PositiveSmallIntegerField()

    def patrimony_necessery_in_period(self, month_quantities, value):
        rate = self.protection_manager.financial_planning.real_gain()
        return numpy.pv(rate, month_quantities, -value)

    def patrimony_necessery_total(self):
        portion_0_to_24_month = self.patrimony_necessery_in_period(
            24, self.value_0_to_24_month)
        portion_24_to_60_month = self.patrimony_necessery_in_period(
            36, self.value_24_to_60_month)
        portion_60_to_120_month = self.patrimony_necessery_in_period(
            60, self.value_60_to_120_month)
        portion_120_to_240_month = self.patrimony_necessery_in_period(
            120, self.value_120_to_240_month)

        total = portion_0_to_24_month + portion_24_to_60_month +\
            portion_60_to_120_month + portion_120_to_240_month

        return total


class EmergencyReserve(models.Model):

    month_of_protection = models.PositiveSmallIntegerField()

    def necessery_value(self):
        regular_cost_monthly = self.protection_manager.financial_planning.\
            cost_manager.total()
        total = self.month_of_protection * regular_cost_monthly

        return total

    def risk_gap(self):
        current_patrimony = self.protection_manager.financial_planning.\
            patrimony.current_net_investment()
        necessery_value = self.necessery_value()
        if current_patrimony < necessery_value:
            total = necessery_value - current_patrimony
        else:
            total = 0

        return total


class ProtectionManager(models.Model):

    financial_planning = models.OneToOneField(
        FinancialPlanning,
        on_delete=models.CASCADE,
        null=True,
        related_name='protection_manager'
    )

    reserve_in_lack = models.OneToOneField(
        ReserveInLack,
        on_delete=models.CASCADE,
        related_name='protection_manager',
    )

    emergency_reserve = models.OneToOneField(
        EmergencyReserve,
        on_delete=models.CASCADE,
        related_name='protection_manager',
    )

    def private_pension_total(self):
        total = self.private_pensions.aggregate(Sum('accumulated'))
        total = (total['accumulated__sum'] or 0)

        return total

    def life_insurances_flow(self):
        duration_flow = self.financial_planning.duration()
        data = [0] * duration_flow
        life_insurances = self.life_insurances.all()

        for life_insurance in life_insurances:
            for index in range(duration_flow):
                if life_insurance.index_end() >= index:
                    data[index] += life_insurance.value_to_pay_annual

        return data


class PrivatePension(models.Model):
    name = models.CharField(max_length=100)
    value_annual = models.FloatField(default=0)
    accumulated = models.FloatField(default=0)
    protection_manager = models.ForeignKey(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='private_pensions')

    def __str__(self):
        return "{name} {value}".format(**self.__dict__)


class LifeInsurance(models.Model):
    name = models.CharField(max_length=100)
    value_to_recive = models.FloatField(default=0)
    value_to_pay_annual = models.FloatField(default=0)
    year_end = models.PositiveSmallIntegerField(null=True)
    redeemable = models.BooleanField()
    has_year_end = models.BooleanField()
    protection_manager = models.ForeignKey(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='life_insurances')

    def index_end(self):
        if self.has_year_end:
            actual_year = datetime.datetime.now().year
            index = self.year_end - actual_year
        else:
            index = self.protection_manager.financial_planning.duration()

        return index

    def __str__(self):
        return "{name} {value}".format(**self.__dict__)

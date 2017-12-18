import datetime
import abc
import numpy
from django.db import models
from patrimony.models import Patrimony
from financial_planning.models import (
    CostManager,
    FinancialPlanning,
)
from lib.profit.profit import actual_rate


class EmergencyReserve(models.Model):

    cost_manager = models.OneToOneField(
        CostManager,
        on_delete=models.CASCADE,
        related_name='emergency_reserve',
    )

    patrimony = models.OneToOneField(
        Patrimony,
        on_delete=models.CASCADE,
        related_name='emergency_reserve',
    )

    mounth_of_protection = models.PositiveSmallIntegerField()

    def necessery_value(self):
        regular_cost_mounthly = self.cost_manager.total()
        total = self.mounth_of_protection * regular_cost_mounthly

        return total

    def risk_gap(self):
        current_patrimony = self.patrimony.current_net_investment()
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
        related_name='protection_manager',
    )

    def life_insurances_flow(self):
        duration_flow = self.financial_planning.duration()
        data = [0] * duration_flow
        life_insurances = self.life_insurances.all()

        for life_insurance in life_insurances:
            for index in range(duration_flow):
                if life_insurance.index_end() >= index:
                    data[index] += life_insurance.value_to_pay_annual

        return data

    def private_pensions_total(self):

        total = self.private_pensions.aggregate(models.Sum('value_annual'))
        total = (total['value_annual__sum'] or 0)

        return total

    def flow(self):

        data = []
        private_pension_total = self.private_pensions_total()
        for element in self.life_insurances_flow():
            data.append(element + private_pension_total)

        return data


class ReserveInLack(models.Model):

    protection_manager = models.OneToOneField(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='reserve_in_lack',
    )

    value_0_to_24_mounth = models.PositiveSmallIntegerField()

    value_24_to_60_mounth = models.PositiveSmallIntegerField()

    value_60_to_120_mounth = models.PositiveSmallIntegerField()

    value_120_to_240_mounth = models.PositiveSmallIntegerField()

    def patrimony_necessery_in_period(self, mounth_quantities, value):
        rate = self.protection_manager.financial_planning.real_gain()
        return numpy.pv(rate, mounth_quantities, -value)

    def patrimony_necessery_total(self):
        portion_0_to_24_mounth = self.patrimony_necessery_in_period(
            24, self.value_0_to_24_mounth)
        portion_24_to_60_mounth = self.patrimony_necessery_in_period(
            36, self.value_24_to_60_mounth)
        portion_60_to_120_mounth = self.patrimony_necessery_in_period(
            60, self.value_60_to_120_mounth)
        portion_120_to_240_mounth = self.patrimony_necessery_in_period(
            120, self.value_120_to_240_mounth)

        total = portion_0_to_24_mounth + portion_24_to_60_mounth +\
            portion_60_to_120_mounth + portion_120_to_240_mounth

        return total


class SuccessionTemplate(models.Model):

    class Meta:
        abstract = True

    __metaclass__ = abc.ABCMeta
    itcmd_tax = models.FloatField(default=0)
    oab_tax = models.FloatField(default=0)
    other_taxes = models.FloatField(default=0)

    @abc.abstractmethod
    def private_pension_total(self):
        """Calculate total private pension"""
        pass

    @abc.abstractmethod
    def life_insurance_to_recive_total(self):
        """Calculate total life_insurance to recive"""
        pass

    @abc.abstractmethod
    def patrimony_total(self):
        """Recover the total patrimony in respective period"""
        pass

    def patrimony_necessery_to_itcmd(self):
        total = self.patrimony_total() * self.itcmd_tax

        return total

    def patrimony_necessery_to_oab(self):
        total = self.patrimony_total() * self.oab_tax

        return total

    def patrimony_necessery_to_other_taxes(self):
        total = self.patrimony_total() * self.other_taxes

        return total

    def patrimony_necessery_total_to_sucession(self):
        total = self.patrimony_necessery_to_itcmd() +\
            self.patrimony_necessery_to_oab() +\
            self.patrimony_necessery_to_other_taxes()

        return total

    def total_to_recive_after_death_without_taxes(self):
        total = self.private_pension_total() +\
            self.life_insurance_to_recive_total()

        return total

    def leftover_after_sucession(self):
        total = self.total_to_recive_after_death_without_taxes() -\
            self.patrimony_necessery_total_to_sucession()

        return total

    def need_for_vialicia(self):
        total = self.leftover_after_sucession() +\
            self.patrimony_total() -\
            self.protection_manager.reserve_in_lack.\
            patrimony_necessery_total()

        return total


class ActualPatrimonySuccession(SuccessionTemplate):

    protection_manager = models.OneToOneField(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='actual_patrimony_succession'
    )

    def private_pension_total(self):
        total = self.protection_manager.private_pensions.aggregate(models.Sum(
            'value'))
        total = (total['value__sum'] or 0)

        return total

    def life_insurance_to_recive_total(self):
        value = self.protection_manager.life_insurances.filter(actual=True).\
            aggregate(models.Sum('value_to_recive'))
        value = (value['value_to_recive__sum'] or 0)

        return value

    def patrimony_total(self):
        return self.protection_manager.financial_planning.patrimony.total()


class IndependencePatrimonySuccession(SuccessionTemplate):

    protection_manager = models.OneToOneField(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='future_patrimony_succession'
    )

    def private_pension_total(self):
        private_pensions = self.protection_manager.private_pensions.all()
        total = 0
        for private_pension in private_pensions:
            total += private_pension.value_moniterized()

        return total

    def life_insurance_to_recive_total(self):
        value = self.protection_manager.life_insurances.aggregate(models.Sum(
            'value_to_recive'))
        value = (value['value_to_recive__sum'] or 0)

        return value

    def patrimony_total(self):
        return self.protection_manager.financial_planning.\
            financial_independence.patrimony_at_end()


class PrivatePension(models.Model):
    name = models.CharField(max_length=100)
    value_annual = models.FloatField(default=0)
    value = models.FloatField(default=0)
    rate = models.FloatField(default=0)
    protection_manager = models.ForeignKey(
        ProtectionManager,
        on_delete=models.CASCADE,
        related_name='private_pensions')

    def __str__(self):
        return "{name} {value_annual} {value}".format(**self.__dict__)

    def real_gain(self):
        return actual_rate(self.rate, self.protection_manager.
                           financial_planning.ipca)

    def value_moniterized(self):
        rate = self.real_gain()
        duration = self.protection_manager.financial_planning.duration()
        value_annual = self.value_annual * -1
        value = self.value * -1
        total_value_moniterized = numpy.fv(rate, duration, value_annual,
                                           value)

        return total_value_moniterized


class LifeInsurance(models.Model):
    name = models.CharField(max_length=100)
    value_to_recive = models.FloatField(default=0)
    value_to_pay_annual = models.FloatField(default=0)
    year_end = models.PositiveSmallIntegerField(null=True)
    redeemable = models.BooleanField()
    actual = models.BooleanField()
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
        string = "{name} {value_to_pay_annual} {value_to_recive}"
        return string.format(**self.__dict__)

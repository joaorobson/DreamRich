from django.db import models
from django.db.models import Sum


class Patrimony(models.Model):
    fgts = models.DecimalField(decimal_places=2, max_digits=8)

    @property
    def current_net_investment(self):
        total_active = self.active_set.all().aggregate(Sum('value'))
        total_arrearage = self.arrearage_set.all().aggregate(Sum('value'))
        total = ((total_active['value__sum'] or 0)
                 - (total_arrearage['value__sum'] or 0))

        return total

    @property
    def current_property_investment(self):
        non_salable_total = self.realestate_set.filter(
            salable=False).aggregate(Sum('value'))
        non_salable_total = (non_salable_total['value__sum'] or 0)

        return non_salable_total

    @property
    def possible_income_generation(self):
        total_company_participation = self.companyparticipation_set.all(
        ).aggregate(Sum('value'))
        total_equipment = self.equipment_set.all().aggregate(Sum('value'))
        total = (total_company_participation['value__sum'] or 0) + \
            (total_equipment['value__sum'] or 0) + self.fgts

        return total

    @property
    def current_monthly_income(self):
        total_value_monthly = self.income_set.all().aggregate(
            Sum('value_monthly'))
        total_value_monthly = total_value_monthly['value_monthly__sum']
        total_vacation = self.income_set.all().aggregate(Sum('vacation'))
        total_vacation = total_vacation['vacation__sum']
        total_thirteenth = self.income_set.all().aggregate(Sum('thirteenth'))
        total_thirteenth = total_thirteenth['thirteenth__sum']
        total_vacation_monthly = total_vacation / 12
        total_thirteenth_monthly = total_thirteenth / 12

        total = total_value_monthly + total_vacation_monthly \
                                    + total_thirteenth_monthly
        total = round(total, 2)

        return total

    @property
    def current_none_investment(self):
        total_movable_property = self.movableproperty_set.all().aggregate(
            Sum('value'))
        total_movable_property = (total_movable_property['value__sum'] or 0)
        salable_total = self.realestate_set.filter(
            salable=True).aggregate(Sum('value'))
        salable_total = (salable_total['value__sum'] or 0)

        total = total_movable_property + salable_total
        return total

    @property
    def total_regular_cost(self):
        regular_cost = self.regularcost
        total_regular_cost = regular_cost.home \
            + regular_cost.electricity_bill + regular_cost.gym \
            + regular_cost.taxes + regular_cost.car_gas \
            + regular_cost.insurance + regular_cost.cellphone \
            + regular_cost.health_insurance + regular_cost.supermarket \
            + regular_cost.housekeeper + regular_cost.beauty \
            + regular_cost.internet + regular_cost.netflix \
            + regular_cost.recreation + regular_cost.meals \
            + regular_cost.appointments + regular_cost.drugstore \
            + regular_cost.extras

        return total_regular_cost


class Active(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class Arrearage(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class RealEstate(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    salable = models.BooleanField()
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class CompanyParticipation(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class LifeInsurance(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    redeemable = models.BooleanField()
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class Income(models.Model):
    source = models.CharField(max_length=100)
    value_monthly = models.DecimalField(decimal_places=2, max_digits=8,
                                        default=0)
    thirteenth = models.DecimalField(decimal_places=2, max_digits=8)
    vacation = models.DecimalField(decimal_places=2, max_digits=8)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class Leftover(models.Model):
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)

    @property
    def leftover(self):
        return (self.patrimony.current_monthly_income -
                self.patrimony.regularcost.total)


class MovableProperty(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    patrimony = models.ForeignKey(Patrimony, on_delete=models.CASCADE)


class RegularCost(models.Model):
    patrimony = models.OneToOneField(
        Patrimony,
        on_delete=models.CASCADE,
        primary_key=True)

    home = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    electricity_bill = models.DecimalField(decimal_places=2, max_digits=8,
                                           default=0)
    gym = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    taxes = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    car_gas = models.DecimalField(decimal_places=2, max_digits=8, default=0)

    insurance = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    cellphone = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    health_insurance = models.DecimalField(decimal_places=2, max_digits=8,
                                           default=0)
    supermarket = models.DecimalField(decimal_places=2, max_digits=8,
                                      default=0)
    housekeeper = models.DecimalField(decimal_places=2, max_digits=8,
                                      default=0)
    beauty = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    internet = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    netflix = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    recreation = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    meals = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    appointments = models.DecimalField(
        decimal_places=2, max_digits=8, default=0)  # consultas
    drugstore = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    extras = models.DecimalField(decimal_places=2, max_digits=8, default=0)

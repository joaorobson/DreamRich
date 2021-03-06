import factory
from . import models
from .choices import AMORTIZATION_CHOICES_LIST


class ActiveTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.ActiveType

    name = factory.Sequence(lambda n: "ActiveType %03d" % n)


class ActiveFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Active

    name = factory.Sequence(lambda n: "Active %03d" % n)
    value = round(351200.00, 2)
    active_type = factory.SubFactory(ActiveTypeFactory)
    rate = factory.Faker('pyfloat')
    equivalent_rate = factory.Faker('pyfloat')


class ActiveManagerFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.ActiveManager

    active = factory.RelatedFactory(ActiveFactory, 'active_manager')


class ArrearageFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Arrearage

    name = factory.Faker('word')
    value = round(30000, 2)
    period = 2
    rate = factory.fuzzy.FuzzyDecimal(100)
    amortization_system = factory.fuzzy.FuzzyChoice(AMORTIZATION_CHOICES_LIST)


class RealEstateFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.RealEstate

    name = factory.Faker('word')
    value = round(121.21, 2)
    salable = False


class MovablePropertyFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.MovableProperty

    name = factory.Faker('word')
    value = round(121.21, 2)


class CompanyParticipationFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.CompanyParticipation

    name = factory.Faker('word')
    value = round(1221.21, 2)


class EquipmentFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Equipment

    name = factory.Faker('word')
    value = round(122.2, 2)


class IncomeFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Income

    source = factory.Faker('word')
    value_monthly = round(51212.2, 2)
    thirteenth = True
    vacation = True


class PatrimonyFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Patrimony

    fgts = round(2.2, 2)
    activemanager = factory.RelatedFactory(ActiveManagerFactory, 'patrimony')
    arrearage = factory.RelatedFactory(ArrearageFactory, 'patrimony')
    real_estate = factory.RelatedFactory(RealEstateFactory, 'patrimony')
    company = factory.RelatedFactory(CompanyParticipationFactory, 'patrimony')
    equipment = factory.RelatedFactory(EquipmentFactory, 'patrimony')
    incomes = factory.RelatedFactory(IncomeFactory, 'patrimony')
    movable_property = factory.RelatedFactory(MovablePropertyFactory,
                                              'patrimony')


class PatrimonyBaseFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Patrimony


class ActiveManagerBaseFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.ActiveManager

    patrimony = factory.SubFactory(PatrimonyBaseFactory)

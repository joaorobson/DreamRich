import factory
from client.factories import ActiveClientFactory
from patrimony.factories import PatrimonyFactory
from goal.factories import GoalManagerFactory, GoalFactory
from . import models


class FinancialIndependenceFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.FinancialIndependence

    age = 60
    duration_of_usufruct = 20
    remain_patrimony = 200000
    rate = factory.Faker('pyfloat')


class CostTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.CostType

    name = factory.Sequence(lambda n: "RegularCost %03d" % n)


class RegularCostFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.RegularCost

    value = factory.Faker('pyint')
    cost_type = factory.SubFactory(CostTypeFactory)


class CostManagerFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.CostManager

    @factory.post_generation
    def _regular_cost(self, create, *unused_args, **unused_kwargs):
        if create:
            return RegularCostFactory.create_batch(18,
                                                   cost_manager=self,
                                                   value=round(12.2, 2))

        return RegularCostFactory.build_batch(18, value=round(12.2, 2))


class FinancialPlanningFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.FinancialPlanning

    active_client = factory.SubFactory(ActiveClientFactory)
    patrimony = factory.SubFactory(PatrimonyFactory)
    financial_independence = factory.SubFactory(FinancialIndependenceFactory)
    goal_manager = factory.SubFactory(GoalManagerFactory)
    cost_manager = factory.SubFactory(CostManagerFactory)
    target_profitability = 1.10
    cdi = round(0.1213, 4)
    ipca = round(0.075, 4)


class GoalMainFactory():

    @staticmethod
    def create():
        financial_planning = FinancialPlanningFactory()
        goal_manager = financial_planning.goal_manager
        GoalFactory.create_batch(8, goal_manager=goal_manager)

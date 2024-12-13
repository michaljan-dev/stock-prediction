from app import db
import ast
import graphene
from graphene import relay
from graphene.relay.node import Node
from app.sinet.core.utils import (
    Helper,
    ExtendedSQLAlchemyObjectType,
    ExtendedSQLAlchemyConnectionField,
    IdField,
)
import importlib
from .models import (
    CrontabSchedule as CrontabModel,
    SchedulerEntry as CrontabScheduleModel,
    Module as ModuleModel,
)


dbsession = db.session()


class Module(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = ModuleModel
        interfaces = (relay.Node,)


class ModuleConnection(relay.Connection):
    class Meta:
        node = Module


class CrontabSchedule(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = CrontabScheduleModel
        interfaces = (relay.Node,)


class CrontabScheduleConnection(relay.Connection):
    class Meta:
        node = CrontabSchedule


class Crontab(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = CrontabModel
        interfaces = (relay.Node,)


class CrontabConnection(relay.Connection):
    class Meta:
        node = Crontab


class RunCronJobType(graphene.ObjectType):

    id = graphene.String()
    result = graphene.String()


class RunCronJob(Node):

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return IdField(cls, *args, **kwargs)

    @classmethod
    def node_resolver(cls, only_type, root, info, id):
        return cls.run_node_from_global_id(info, id, only_type=only_type)

    @classmethod
    def run_node_from_global_id(cls, info, global_id, only_type=None):
        try:
            _type, _id = cls.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
        except Exception:
            return None
        crontab_schedule = CrontabScheduleModel.query.get(_id)

        package, classname = crontab_schedule.task.rsplit(".", 1)
        args = ast.literal_eval(crontab_schedule.arguments)
        kwargs = ast.literal_eval(crontab_schedule.keyword_arguments)

        try:
            handler_result = getattr(importlib.import_module(package), classname)(
                *args, **kwargs
            )
        except NotImplementedError:
            handler_result = "error"

        return RunCronJobType(result=handler_result, id=_id)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    modules = ExtendedSQLAlchemyConnectionField(Module)
    crontab_schedule = ExtendedSQLAlchemyConnectionField(CrontabSchedule)
    crontab = ExtendedSQLAlchemyConnectionField(Crontab)
    run_cron_job = RunCronJob.Field(RunCronJobType)


# graphql mutations
class CrontabMutation(graphene.Mutation):

    crontab = graphene.Field(lambda: Crontab)

    class Arguments:

        crontab = graphene.Field(lambda: Crontab)

    def mutate(self, info, **input):
        data = Helper.input_to_dictionary(input)
        # aclResourcePermission = input.get('aclResourcePermission')

        crontab = CrontabModel(**data)
        dbsession.add(crontab)
        dbsession.commit()

        return CrontabMutation(crontab=crontab)


class Mutation(graphene.ObjectType):
    crontab_d = CrontabMutation.Arguments()

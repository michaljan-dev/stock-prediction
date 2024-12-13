import base64
from functools import partial
import graphene
from graphene.relay import Connection
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene.types import Int
from graphene.types.generic import GenericScalar
from graphene.types import ID, Field
from graphql_relay.node.node import from_global_id
import json
from sqlalchemy.sql import or_, not_


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = Int()

    @staticmethod
    def resolve_total_count(self, info, *args, **kwargs):
        return self.iterable.offset(None).limit(None).count()


class ExtendedSQLAlchemyObjectType(SQLAlchemyObjectType):
    class Meta:
        abstract = True

    original_id = graphene.String(source="id")

    def resolve_original_id(self, info, *args, **kwargs):
        return self.id

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        registry=None,
        skip_registry=False,
        only_fields=(),
        exclude_fields=(),
        connection=None,
        connection_class=None,
        use_connection=None,
        interfaces=(),
        id=None,
        _meta=None,
        **options
    ):
        # Force it to use the countable connection
        countable_conn = connection or ExtendedConnection.create_type(
            "{}Connection".format(model.__name__), node=cls
        )

        super(ExtendedSQLAlchemyObjectType, cls).__init_subclass_with_meta__(
            model,
            registry,
            skip_registry,
            only_fields,
            exclude_fields,
            countable_conn,
            connection_class,
            use_connection,
            interfaces,
            id,
            _meta,
            **options
        )


class ExtendedSQLAlchemyConnectionField(SQLAlchemyConnectionField):
    RELAY_ARGS = ["first", "last", "before", "after"]

    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("page_size", Int())
        kwargs.setdefault("page", Int())
        kwargs.setdefault("filters", GenericScalar())
        kwargs.setdefault("order", GenericScalar())
        super(ExtendedSQLAlchemyConnectionField, self).__init__(type, *args, **kwargs)

    @classmethod
    def get_query(cls, model, info, **args):
        query = super(ExtendedSQLAlchemyConnectionField, cls).get_query(
            model, info, **args
        )
        if args.get("filters"):
            query = filterQuery(query, model, args["filters"])

        if args.get("order"):
            query = orderQuery(query, model, args["order"])
        # pagination
        page_size = None
        if args.get("page_size"):
            page_size = args["page_size"]
            query = query.limit(page_size)
        if args.get("page"):
            page = args["page"] - 1
            query = query.offset(page * page_size)

        return query


def orderQuery(query, model, order):
    orders = json.loads(order)

    for order in orders:
        if isinstance(order, (dict,)):
            c = getattr(model, order.get("key"))
            if order.get("direction") == "desc":
                query = query.order_by(c.desc())
            if order.get("direction") == "asc":
                query = query.order_by(c.asc())

    return query


def filterQuery(query, model, filters):
    filters = json.loads(filters)
    for filter in filters:
        conditions = []
        if isinstance(filter, (list,)):
            for filt in filter:
                conditions = constructConditions(conditions, filt, model)
            condition = or_(*conditions)
            query = query.filter(condition)
        if isinstance(filter, (dict,)):
            conditions = constructConditions(conditions, filter, model)
            query = query.filter(*conditions)
    return query


def constructConditions(conditions, filter, model):
    c = getattr(model, filter.get("key"))
    v = filter.get("val")
    op = filter.get("op")
    if filter.get("pk"):
        (table_name, v) = base64.b64decode(v.encode()).decode().split(":")

    if not c or not op or not v:
        pass
    if op == "==":
        conditions.append(c == v)
    if op == "!=":
        conditions.append(c != v)
    if op == "<=":
        conditions.append(c <= v)
    if op == ">=":
        conditions.append(c >= v)
    if op == ">":
        conditions.append(c > v)
    if op == "<":
        conditions.append(c < v)
    if op == "starts":
        conditions.append(c.ilike(v + "%"))
    if op == "ends":
        conditions.append(c.ilike("%" + v))
    if op == "contains":
        conditions.append(c.contains(v))
    if op == "in":
        conditions.append(c.in_(v))
    if op == "notin":
        conditions.append(not_(c.in_(v)))
    return conditions


# single id field
class IdField(Field):
    def __init__(self, node, type=False, deprecation_reason=None, name=None, **kwargs):

        self.node_type = node
        self.field_type = type

        super(IdField, self).__init__(
            # If we don's specify a type, the field type will be the node
            # interface
            type or node,
            description="The ID of the object",
            id=ID(required=True),
        )

    def get_resolver(self, parent_resolver):
        return partial(self.node_type.node_resolver, self.field_type)


# filters field
class FilterField(Field):
    def __init__(self, node, type=False, deprecation_reason=None, name=None, **kwargs):

        self.node_type = node
        self.field_type = type
        super(FilterField, self).__init__(
            # If we don's specify a type, the field type will be the node
            # interface
            type or node,
            description="Scalar json format",
            filters=GenericScalar(required=True),
        )

    def get_resolver(self, parent_resolver):
        return partial(self.node_type.node_resolver, self.field_type)


# to store aplication dynamic global variables
class Config:
    def get_value(self, key, scope=None, **args):
        return self.key

    def set_value(self, key, scope=None, **args):
        return self.key


# some helper methods
class Helper:
    def input_to_dictionary(self, input):
        """Method to convert Graphene inputs into dictionary"""
        dictionary = {}
        for key in input:
            if key[-2:] == "id":
                input[key] = from_global_id(input[key])[1]
                dictionary[key] = input[key]
            dictionary[key] = input[key]
        return dictionary

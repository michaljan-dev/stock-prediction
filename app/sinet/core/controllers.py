# Import flask dependencies
from app import app
from flask import Blueprint
from flask_graphql import GraphQLView
import graphene
import importlib
from inspect import getmembers, isclass
import os

project_parent = os.path.abspath(".") + "/app"

# init modules
modules = ["sinet__core", "sinet__user", "sinet__market"]


class GraphQLAbstract(graphene.ObjectType):
    pass


graphql_queries_base_classes = [GraphQLAbstract]
graphql_mutations_base_classes = [GraphQLAbstract]

# import modules components
for module in modules:
    try:
        module = module.split("__")
        # controllers
        importlib.import_module(f"app.{module[0]}.{module[1]}.controllers")
        # graphql
        module_schema = importlib.import_module(f"app.{module[0]}.{module[1]}.schema")
        if module_schema:
            classes = [x for x in getmembers(module_schema, isclass)]
            queries = [x[1] for x in classes if "Query" in x[0]]
            mutations = [x[1] for x in classes if "Mutation" in x[0]]
            graphql_queries_base_classes += queries
            graphql_mutations_base_classes += mutations

    except ModuleNotFoundError:
        pass

# init graphql
graphql_queries_base_classes = graphql_queries_base_classes[::-1]
graphql_mutations_base_classes = graphql_mutations_base_classes[::-1]

properties_queries = {}
properties_mutations = {}
for base_class in graphql_queries_base_classes:
    properties_queries.update(base_class.__dict__["_meta"].fields)

for base_class in graphql_mutations_base_classes:
    properties_mutations.update(base_class.__dict__["_meta"].fields)

Queries = type("Queries", tuple(graphql_queries_base_classes), properties_queries)
Mutations = type(
    "Mutations", tuple(graphql_mutations_base_classes), properties_mutations
)

schema = graphene.Schema(query=Queries, mutation=Mutations)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=schema, graphiql=True  # for having the GraphiQL interface
    ),
)


sinet_core = Blueprint("sinet_core", __name__, url_prefix="/sinet/core")
app.register_blueprint(sinet_core)

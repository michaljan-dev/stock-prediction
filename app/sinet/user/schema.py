import graphene
from graphene import relay
from app.sinet.core.utils import (
    ExtendedSQLAlchemyObjectType,
    ExtendedSQLAlchemyConnectionField,
)
from .models import (
    User as UserModel,
    Role as RoleModel,
    AclResourcePermission as AclResourcePermissionModel,
)
from .models import AclPermission as AclPermissionModel, AclResource as AclResourceModel
from graphene.types import Int
from graphene.types.generic import GenericScalar
from app import db

dbsession = db.session()


# graphql queries
class User(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node,)
        exclude_fields = "password"


class UserConnection(relay.Connection):
    class Meta:
        node = User


class Role(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = RoleModel
        interfaces = (relay.Node,)


class RoleConnection(relay.Connection):
    class Meta:
        node = Role


class AclPermission(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = AclPermissionModel
        interfaces = (relay.Node,)


class AclPermissionConnection(relay.Connection):
    class Meta:
        node = AclPermission


class AclResource(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = AclResourceModel
        interfaces = (relay.Node,)


class AclResourceConnection(relay.Connection):
    class Meta:
        node = AclResource


class AclResourcePermission(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = AclResourcePermissionModel
        interfaces = (relay.Node,)


class AclResourcePermissionConnection(relay.Connection):
    class Meta:
        node = AclResourcePermission


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    users = ExtendedSQLAlchemyConnectionField(User)
    roles = ExtendedSQLAlchemyConnectionField(Role)
    acl_permission = ExtendedSQLAlchemyConnectionField(AclPermission)
    acl_resource = ExtendedSQLAlchemyConnectionField(AclResource)


# graphql mutations
class RoleAclResourcePermission(graphene.Mutation):

    role = graphene.Field(lambda: Role)

    class Arguments:
        role_id = Int(required=True)
        aclResourcePermission = GenericScalar(required=True)

    def mutate(self, info, **input):
        role_id = input.get("role_id")
        aclResourcePermission = input.get("aclResourcePermission")

        aclResourcePermissions = []

        for rsperm in aclResourcePermission:
            acl_permission_id = rsperm.get("acl_permission_id")
            acl_resource_id = rsperm.get("acl_resource_id")
            aclResourcePermissions.append(
                AclResourcePermissionModel(
                    role_id=role_id,
                    acl_permission_id=acl_permission_id,
                    acl_resource_id=acl_resource_id,
                )
            )

        dbsession.query(AclResourcePermissionModel).filter_by(role_id=role_id).delete()
        dbsession.add_all(aclResourcePermissions)
        try:
            dbsession.commit()

        except Exception:
            dbsession.rollback()
            raise

        return RoleAclResourcePermission()


class Mutation(graphene.ObjectType):
    role_acl_resource_permission = RoleAclResourcePermission.Field()

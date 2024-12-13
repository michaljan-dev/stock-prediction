# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from sqlalchemy.orm import relationship, backref


TEMP_USERNAME = "admin"
TEMP_PASSWORD = "admin"
TEMP_EMAIL = "admin@admin.com"


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class User(Base):

    __tablename__ = "user"

    email = db.Column(db.String(128), nullable=False, unique=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(192), nullable=False)
    is_active = db.Column(db.Integer, default=1)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    roles = relationship("Role", secondary="user_role", lazy="joined")

    # New instance instantiation procedure
    def __init__(self, email, username, password):

        self.email = email
        self.username = username
        self.password = password

    def getResourcePermissions(self):
        acl_permission = AclPermission.query.all()
        acl_resource = AclResource.query.all()
        acl_resource_resource = {}
        acl_permission_resource = {}
        for ar in acl_resource:
            acl_resource_resource.update({ar.id: {"name": ar.name}})
        for ar in acl_permission:
            acl_permission_resource.update({ar.id: {"name": ar.name}})

        ap = {}
        app = {}
        i = 0
        for role in self.roles:
            for acl_resource_permission in role.acl_resources_permission:
                ap = {}
                ap = acl_resource_resource[acl_resource_permission.acl_resource_id][
                    "name"
                ]
                rs = acl_permission_resource[acl_resource_permission.acl_permission_id][
                    "name"
                ]
                if not (app.get(rs)):
                    app[rs] = {}
                app[rs][i] = ap
                i = i + 1

        return app


class Role(Base):

    __tablename__ = "role"

    role = db.Column(db.String(128), nullable=False, unique=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    is_system = db.Column(db.Integer, default=0)

    users = relationship("User", secondary="user_role")
    acl_resources_permission = relationship("AclResourcePermission", lazy="joined")

    # New instance instantiation procedure
    def __init__(self, role, name, is_system):

        self.role = role
        self.name = name
        self.is_system = is_system


class UserRole(Base):

    __tablename__ = "user_role"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)

    user = relationship(User, backref=backref("user_assoc"))
    role = relationship(Role, backref=backref("role_assoc"))

    # New instance instantiation procedure
    def __init__(self, user_id, role_id):

        self.user_id = user_id
        self.role_id = role_id


class AclPermission(Base):

    __tablename__ = "acl_permission"

    # User Name
    # Identification Data: email & password
    name = db.Column(db.String(128), nullable=False)

    # New instance instantiation procedure
    def __init__(self, name):

        self.name = name


class AclResource(Base):

    __tablename__ = "acl_resource"

    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    permissions = db.Column(db.String(256), nullable=True)

    # New instance instantiation procedure
    def __init__(self, name):

        self.name = name


class AclResourcePermission(Base):

    __tablename__ = "acl_resource_permission"

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    acl_resource_id = db.Column(
        db.Integer, db.ForeignKey("acl_resource.id"), nullable=False
    )
    acl_permission_id = db.Column(
        db.Integer, db.ForeignKey("acl_permission.id"), nullable=False
    )

    def __init__(self, role_id, acl_resource_id, acl_permission_id):

        self.role_id = role_id
        self.acl_resource_id = acl_resource_id
        self.acl_permission_id = acl_permission_id


class UserSession(Base):

    __tablename__ = "user_session"

    session = db.Column(db.String(128), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_expired = db.Column(db.DateTime, default=db.func.current_timestamp())

    # New instance instantiation procedure
    def __init__(self, session, date_created, date_expired):

        self.session = session
        self.date_created = date_created
        self.date_expired = date_expired


@db.event.listens_for(User.__table__, "after_create")
def user_after_create(*args, **kwargs):
    # !!!temp passwword is in plain text, not encrypted not hashed
    db.session.add(
        User(username=TEMP_USERNAME, email=TEMP_EMAIL, password=TEMP_PASSWORD)
    )
    db.session.commit()


@db.event.listens_for(Role.__table__, "after_create")
def role_after_create(*args, **kwargs):
    db.session.add(Role(role="anonymous", name="Anonymous", is_system=1))
    db.session.add(Role(role="authenticated", name="Authenticated", is_system=1))
    db.session.add(Role(role="administrator", name="Administrator", is_system=1))
    db.session.commit()


@db.event.listens_for(AclPermission.__table__, "after_create")
def aclPermission_after_create(*args, **kwargs):
    db.session.add(AclPermission(name="all"))
    db.session.add(AclPermission(name="insert"))
    db.session.add(AclPermission(name="view"))
    db.session.add(AclPermission(name="edit"))
    db.session.add(AclPermission(name="delete"))
    db.session.commit()

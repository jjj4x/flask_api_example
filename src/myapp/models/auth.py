"""MYAPP authentication and authorization models."""
from flask_security import UserMixin, RoleMixin, hash_password

from myapp import db


class UserModel(db.Model, UserMixin):
    """User model."""

    __tablename__ = 'user'
    __table_args__ = {
        'comment': 'Users',
    }

    id = db.Column(  # noqa: WPS125
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    username = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )
    email = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )
    password = db.Column(
        db.String,
        nullable=False,
    )
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )
    confirmed_at = db.Column(
        db.TIMESTAMP,
        nullable=True,
        default=None,
    )

    roles = db.relationship(
        'RoleModel',
        secondary='user_roles',
        lazy='joined',
    )

    @classmethod
    def create_new_user(cls, **kwargs):
        """Create a new user."""
        password = kwargs.get('password')
        if password:
            kwargs['password'] = hash_password(password)
        else:
            kwargs['active'] = False
        return cls(**kwargs)

    def set_password(self, password):
        """Set hashed password."""
        self.password = hash_password(password)


class RoleModel(db.Model, RoleMixin):
    """Role model."""

    __tablename__ = 'role'
    __table_args__ = {
        'comment': 'Roles',
    }

    id = db.Column(  # noqa: WPS125
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )

    users = db.relationship(
        'UserModel',
        secondary='user_roles',
    )
    permissions = db.relationship(
        'PermissionModel',
        secondary='role_permissions',
        lazy='joined',
    )

    def __str__(self):
        """
        Represent as string.

        :return: username
        """
        return self.name


class PermissionModel(db.Model):
    """Permission model."""

    __tablename__ = 'permission'
    __table_args__ = {
        'comment': 'Permissions',
    }

    id = db.Column(  # noqa: WPS125
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )

    roles = db.relationship(
        'RoleModel',
        secondary='role_permissions',
    )

    def __str__(self):
        """
        Represent as string.

        :return: permission name.
        """
        return self.name

    def __eq__(self, other):
        """
        Check equality.

        :param other: other permission
        :return: boolean
        """
        return self.name in {other, getattr(other, 'name', None)}

    def __ne__(self, other):
        """
        Check inequality.

        :param other: other permission
        :return: boolean
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Calculate permission hash.

        :return: hash of name
        """
        return hash(self.name)

    @classmethod
    def from_json(cls, data):
        """
        Create permission from JSON.

        :param data: JSON data
        :return: permission model
        """
        # noinspection PyArgumentList
        return cls(**data)

    def to_json(self):
        """
        Convert permission into JSON.

        :return: JSON representation.
        """
        return {
            'id': self.id,
            'name': self.name,
        }


user_roles = db.Table(
    'user_roles',
    db.Column(
        'u_id',
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True,
    ),
    db.Column(
        'r_id',
        db.Integer,
        db.ForeignKey('role.id'),
        primary_key=True,
    ),
)

role_permissions = db.Table(
    'role_permissions',
    db.Column(
        'r_id',
        db.Integer,
        db.ForeignKey('role.id'),
        primary_key=True,
    ),
    db.Column(
        'p_id',
        db.Integer,
        db.ForeignKey('permission.id'),
        primary_key=True,
    ),
)

__version__ = '0.1.0'


class PermissionError(Exception):
    """Raised when permission is invalid."""
    pass


class AuthorizationError(Exception):
    """Raised when user has no permission."""
    pass


class Authorization(object):
    """Container of authorization rules and checker of permissions."""
    def __init__(self):
        self._rules = {}

    def add_rule(self, target_class, rule_class):
        """Adds an authorization rule for a specified class of objects.

        :param target_class: class of objects.
        :param rule_class: class of authorization rule.
        """
        self._rules[target_class] = rule_class

    def rule_for(self, target_class):
        """Decorates and adds an authorization rule for a specified class of objects.

        :param target_class: a class of objects.
        """
        def decorator(rule_class):
            self.add_rule(target_class, rule_class)
            return rule_class
        return decorator

    def check(self, user, permission, obj):
        """Raises AuthorizationError when a user has no permission.

        :param user: a user.
        :param permission: permission to check.
        :param obj: an object.
        """
        if not self.allows(user, permission, obj):
            raise AuthorizationError()

    def allows(self, user, permission, obj):
        """Checks that a user has permission for an object.
        Returns True of False.

        :param user: a user.
        :param permission: permission to check.
        :param obj: an object.
        """
        rule = self._get_rule(obj)

        try:
            checker = self._get_checker(rule, permission)
        except AttributeError:
            raise PermissionError()

        return checker(user, obj)

    def _get_rule(self, obj):
        return self._rules[type(obj)]()

    @staticmethod
    def _get_checker(rule, permission):
        return getattr(rule, 'can_{}'.format(permission))

    def get_permissions(self, user, obj):
        """Returns permissions set of a user for an object.

        :param user: a user.
        :param obj: an object.
        """
        rule = self._get_rule(obj)

        all_permissions = (
            attr[len('can_'):] for attr in dir(rule)
            if attr.startswith('can_')
        )

        return set(
            permission for permission in all_permissions
            if self.allows(user, permission, obj)
        )

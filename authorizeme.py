from collections import Iterable


__version__ = '0.2'


try:
    basestring
except NameError:
    basestring = str


class PermissionError(Exception):
    """Raised when permission is invalid."""


class RuleError(Exception):
    """Raised when there is no authorization rule for class of given object."""


class AuthorizationError(Exception):
    """Raised when user has no permission."""


class _Nothing(object):
    """Default class to associate authorization rules with."""


_nothing = _Nothing()  # default object to check permission for


class Authorization(object):
    """Container of authorization rules and checker of permissions."""
    def __init__(self):
        self._rules = {}

    def add_rule(self, rule_class, target_class=_Nothing):
        """Adds an authorization rule.

        :param rule_class: a class of authorization rule.
        :param target_class: (optional) a class
            or an iterable with classes to associate the rule with.
        """
        if isinstance(target_class, Iterable):
            for cls in target_class:
                self._rules[cls] = rule_class
        else:
            self._rules[target_class] = rule_class

    def rule_for(self, target_class):
        """Decorates and adds an authorization rule
        for a specified class(es) of objects.

        :param target_class: a class or an iterable with classes
            to associate the rule with.
        """
        def decorator(rule_class):
            self.add_rule(rule_class, target_class)
            return rule_class
        return decorator

    def rule(self):
        """Decorates and adds an authorization rule."""
        return self.rule_for(_Nothing)

    def check(self, user, permission, obj=_nothing):
        """Raises AuthorizationError when a user has no permission.

        :param user: a user.
        :param permission: permission to check.
        :param obj: (optional) an object to check permission for.
        """
        if not self.allows(user, permission, obj):
            raise AuthorizationError(
                'Can\'t {} object of class {}'.format(
                    permission, type(obj)))

    def allows(self, user, permission, obj=_nothing):
        """Checks that a user has permission. Returns True or False.

        :param user: a user.
        :param permission: permission to check.
        :param obj: (optional) an object to check permission for.
        """
        rule = self._get_rule(obj)

        if not isinstance(permission, basestring):
            return all(
                self._use_rule(rule, user, perm, obj)
                for perm in permission
            )

        return self._use_rule(rule, user, permission, obj)

    def _get_rule(self, obj):
        try:
            rule_class = self._rules[type(obj)]
        except KeyError:
            raise RuleError(
                'There is no authorization rule '
                'for class {}'.format(type(obj))
            )

        return rule_class()

    def _use_rule(self, rule, user, permission, obj):
        try:
            checker = self._get_checker(rule, permission)
        except AttributeError:
            raise PermissionError(
                'Unknown permission "{}" for object '
                'of class {}'.format(permission, type(obj))
            )

        if obj is _nothing:
            return checker(user)

        return checker(user, obj)

    @staticmethod
    def _get_checker(rule, permission):
        return getattr(rule, 'can_{}'.format(permission))

    def get_permissions(self, user, obj=_nothing):
        """Returns permissions of a user.

        :param user: a user.
        :param obj: (optional) an object to get permissions for.
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

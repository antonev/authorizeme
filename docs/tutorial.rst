.. _tutorial:

Getting Started with AuthorizeMe
================================


Installation
------------

Firstly, we need to install AuthorizeMe:

.. code-block:: bash

    $ pip install authorizeme


Creating Authorization Object
-----------------------------

Authorization object is a container for authorization rules and checker
of users permissions. We need to create at least one authorization object::

    from authorizeme import Authorization

    authorization = Authorization()


Adding Authorization Rules
--------------------------

Authorization rule is an object that has permission checks.
Permission check is a method with name starting with 'can\_'.
Other part of the method name matches with a permission.

Example of authorization rule that checks permissions 'read', 'edit',
and 'rate' for objects of class Article::

    @authorization.rule_for(Article)
    def ArticleRule(object):
        def can_read(self, user, obj):
            return True

        def can_edit(self, user, obj):
            return user is obj.author

        def can_rate(self, user, obj):
            return user is not obj.author


Also, authorization rule can be added with add_rule method::

    def ArticleRule(object):
        def can_read(self, user, obj):
            return True

        def can_edit(self, user, obj):
            return user is obj.author

        def can_rate(self, user, obj):
            return user is not obj.author

    authorization.add_rule(ArticleRule, Article)


Finally, we have this authorization rule:

- everyone can read an article,
- only article's author can edit it,
- everyone except article's author can rate it.


One authorization rule can be associated with many classes::

    @authorization.rule_for([BookReview, MovieReview])
    class ArticleRule(object):
        'Permissions checks...'


Example without decorator::

    class ArticleRule(object):
        'Permissions checks...'

    authorization.add_rule(ArticleRule, [BookReview, MovieReview])


Also, authorization rule can be associated with nothing::

    @authorization.rule
    class AuthorizationRule(object):
        def can_add_article(self, user):
            return user.is_writer


Example without decorator::

    class AuthorizationRule(object):
        def can_add_article(self, user):
            return user.is_writer

    authorization.add_rule(AuthorizationRule)


Checking Permissions
--------------------

There are two methods to check permissions::
    
    authorization.allows(user, 'edit', article)
    # returns True or False

    authorization.check(user, 'edit', article)
    # raises AuthorizationError if user has no permission


Multiple permissions can be checked at once::

    authorization.allows(user, ['read', 'edit'], article)
    # returns True only when user has all permissions

    authorization.check(user, ['read', 'edit'], article)
    # raises AuthorizationError when user has no at least one permission


Also, if for some reason you want to get all user
permissions for an object, you can do this::

    permissions = authorization.get_permissions(user, article)


An object is not required when authorization rule is associated with nothing::

    authorization.allows(user, 'add_article')
    authorization.check(user, 'add_article')
    permissions = authorization.get_permissions(user)

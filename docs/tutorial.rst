.. _tutorial:

Getting Started with AuthorizeMe
================================


Installation
------------

Firstly, we need to install AuthorizeMe:

.. code-block:: bash

    pip install authorizeme


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

    authorization.add_rule(Article, ArticleRule)


Finally, we have this authorization rule:

- everyone can read an article,
- only article's author can edit it,
- everyone except article's author can rate it. 


Checking Permissions
--------------------

There are two methods to check permissions::
    
    authorization.allows(user, 'edit', article)
    # returns True or False

    authorization.check(user, 'edit', article)
    # raises AuthorizationError if user has no permission


Also, if for some reason you want to get all user
permissions for an object, you can do this::

    permissions = authorization.get_permissions(user, article)

import pytest


class Blog(object):
    def __init__(self, writers=None):
        self.writers = writers or []


class User(object):
    def __init__(self, is_admin=False):
        self.is_admin = is_admin


class Article(object):
    def __init__(self, author):
        self.author = author


class BookReview(Article):
    pass


class MovieReview(Article):
    pass


@pytest.fixture(params=['declarative', 'imperative'])
def authorization(request):
    configuration_type = request.param

    from authorizeme import Authorization

    class AppRule(object):
        def can_add_blog(self, user):
            return user.is_admin

    class BlogRule(object):
        def can_add_article(self, user, obj):
            return user in obj.writers

        def can_add_author(self, user, obj):
            return user.is_admin

    class ArticleRule(object):
        def can_read(self, user, obj):
            return True

        def can_change(self, user, obj):
            return obj.author is user

        def can_rate(self, user, obj):
            return obj.author is not user

    authz = Authorization()

    if configuration_type == 'declarative':
        authz.rule()(AppRule)
        authz.rule_for(Article)(ArticleRule)
        authz.rule_for([BookReview, MovieReview])(ArticleRule)
        authz.rule_for(Blog)(BlogRule)
    else:
        authz.add_rule(AppRule)
        authz.add_rule(ArticleRule, Article)
        authz.add_rule(ArticleRule, [BookReview, MovieReview])
        authz.add_rule(BlogRule, Blog)

    return authz


@pytest.fixture(params=[Article, BookReview, MovieReview])
def objects(request):
    article_class = request.param
    writer1, writer2 = User(), User()

    return {
        'blog': Blog(writers=[writer1, writer2]),
        'reader': User(),
        'writer1': writer1,
        'writer1_article': article_class(author=writer1),
        'writer2': writer2,
        'writer2_article': article_class(author=writer2),
    }


combinations = [
    # user, target, permission, result
    ('reader', 'blog', 'add_article', False),
    ('writer1', 'blog', 'add_article', True),
    ('writer1', 'writer1_article', 'read', True),
    ('writer1', 'writer1_article', 'change', True),
    ('writer1', 'writer1_article', 'rate', False),
    ('writer1', 'writer1_article', ['read', 'change'], True),
    ('writer1', 'writer1_article', ['read', 'change', 'rate'], False),
    ('writer1', 'writer2_article', 'read', True),
    ('writer1', 'writer2_article', 'change', False),
    ('writer1', 'writer2_article', 'rate', True),
    ('writer2', 'writer1_article', 'read', True),
    ('writer2', 'writer1_article', 'change', False),
    ('writer2', 'writer1_article', 'rate', True),
    ('writer2', 'writer2_article', 'read', True),
    ('writer2', 'writer2_article', 'change', True),
    ('writer2', 'writer2_article', 'rate', False),
    ('writer2', 'writer2_article', ['read', 'change'], True),
    ('writer2', 'writer2_article', ['read', 'change', 'rate'], False),
]


@pytest.mark.parametrize(
    'user_key, target_key, permission, result', combinations)
def test_allows(
        authorization, objects, user_key, target_key, permission, result):
    user = objects[user_key]
    target = objects[target_key]
    assert authorization.allows(user, permission, target) is result


@pytest.mark.parametrize(
    'user_key, target_key, permission, result', combinations)
def test_check(
        authorization, objects, user_key, target_key, permission, result):
    from authorizeme import AuthorizationError

    user = objects[user_key]
    target = objects[target_key]

    try:
        authorization.check(user, permission, target)
    except AuthorizationError:
        error_raised = True
    else:
        error_raised = False

    assert result is not error_raised


def test_rule_without_associated_class(authorization):
    admin = User(is_admin=True)
    assert authorization.allows(admin, 'add_blog')


@pytest.mark.parametrize('user_key, article_key, permissions', [
    ('writer1', 'writer1_article', {'read', 'change'}),
    ('writer1', 'writer2_article', {'read', 'rate'}),
    ('writer2', 'writer1_article', {'read', 'rate'}),
    ('writer2', 'writer2_article', {'read', 'change'}),
])
def test_get_permissions(
        authorization, objects, user_key, article_key, permissions):
    user = objects[user_key]
    article = objects[article_key]
    assert authorization.get_permissions(user, article) == permissions


def test_get_permissions_without_obj(authorization):
    admin = User(is_admin=True)
    assert authorization.get_permissions(admin) == {'add_blog'}


@pytest.fixture
def article():
    return Article(author=User())


def test_unknown_permission(authorization, article):
    from authorizeme import PermissionError

    with pytest.raises(PermissionError):
        authorization.allows(article.author, 'unknown_permission', article)


def test_unknown_permission_check(authorization, article):
    from authorizeme import PermissionError

    with pytest.raises(PermissionError):
        authorization.check(article.author, 'unknown_permission', article)


def test_unknown_class(article):
    from authorizeme import Authorization, RuleError

    authorization = Authorization()

    with pytest.raises(RuleError):
        authorization.allows(article.author, 'edit', article)


def test_unknown_class_check(article):
    from authorizeme import Authorization, RuleError

    authorization = Authorization()

    with pytest.raises(RuleError):
        authorization.allows(article.author, 'edit', article)

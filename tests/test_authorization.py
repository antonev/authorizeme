import pytest


class Blog(object):
    pass


class User(object):
    def __init__(self, is_writer):
        self.is_writer = is_writer


class Article(object):
    def __init__(self, author):
        self.author = author


@pytest.fixture(params=[
    {'configuration_type': 'declarative'},
    {'configuration_type': 'imperative'},
])
def authorization(request):
    from authorizeme import Authorization

    class BlogRule(object):
        def can_add_article(self, user, obj):
            return user.is_writer

    class ArticleRule(object):
        def can_read(self, user, obj):
            return True

        def can_change(self, user, obj):
            return obj.author is user

        def can_rate(self, user, obj):
            return obj.author is not user

    authz = Authorization()

    if request.param['configuration_type'] == 'declarative':
        authz.rule_for(Article)(ArticleRule)
        authz.rule_for(Blog)(BlogRule)
    else:
        authz.add_rule(Article, ArticleRule)
        authz.add_rule(Blog, BlogRule)

    return authz


@pytest.fixture
def objects():
    writer1, writer2 = User(is_writer=True), User(is_writer=True)

    return {
        'blog': Blog(),
        'reader': User(is_writer=False),
        'writer1': writer1,
        'writer1_article': Article(author=writer1),
        'writer2': writer2,
        'writer2_article': Article(author=writer2),
    }


combinations = [
    # user, target, permission, result
    ('reader', 'blog', 'add_article', False),
    ('writer1', 'blog', 'add_article', True),
    ('writer1', 'writer1_article', 'read', True),
    ('writer1', 'writer1_article', 'change', True),
    ('writer1', 'writer1_article', 'rate', False),
    ('writer1', 'writer2_article', 'read', True),
    ('writer1', 'writer2_article', 'change', False),
    ('writer1', 'writer2_article', 'rate', True),
    ('writer2', 'writer1_article', 'read', True),
    ('writer2', 'writer1_article', 'change', False),
    ('writer2', 'writer1_article', 'rate', True),
    ('writer2', 'writer2_article', 'read', True),
    ('writer2', 'writer2_article', 'change', True),
    ('writer2', 'writer2_article', 'rate', False),
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


@pytest.fixture
def article():
    return Article(author=User(is_writer=True))


def test_unknown_permission(authorization, article):
    from authorizeme import PermissionError

    with pytest.raises(PermissionError):
        authorization.allows(article.author, 'unknown_permission', article)


def test_unknown_permission_check(authorization, article):
    from authorizeme import PermissionError

    with pytest.raises(PermissionError):
        authorization.check(article.author, 'unknown_permission', article)

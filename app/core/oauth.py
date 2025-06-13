from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

oauth = OAuth()

# Register Google OAuth
oauth.register(
    name='google',
    client_id=settings.google.google_client_id,
    client_secret=settings.google.google_client_secret,
    server_metadata_url=(
        'https://accounts.google.com/.well-known/openid-configuration'
    ),
    redirect_uri=settings.google.google_redirect_uri,
    client_kwargs={
        'scope': 'openid email profile',
    },
    metadata_cache_ttl=0,
)

# Register Yandex OAuth
oauth.register(
    name='yandex',
    client_id=settings.yandex.yandex_client_id,
    client_secret=settings.yandex.yandex_client_secret,
    authorize_url='https://oauth.yandex.ru/authorize',
    token_url='https://oauth.yandex.ru/token',
    userinfo_endpoint='https://login.yandex.ru/info',
    redirect_uri=settings.yandex.yandex_redirect_uri,
    client_kwargs={
        'scope': 'login:email',
    },
)

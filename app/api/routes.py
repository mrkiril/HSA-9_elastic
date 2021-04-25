from aiohttp import web

from . import views

routes = [
    # web.view("/article/{article_id}", views.ArticleView, name="article"),
    # web.view("/articles", views.ArticlesView, name="articles"),

    web.view("/healthz", views.HealthzCheck, name="health-check"),
    web.view("/favicon.ico", views.Favicon, name="favicon"),
    web.view("/static/{folder}/{filename}", views.FileView, name="file_view"),
    web.view("/api/search", views.SearchView, name="search_view"),
]

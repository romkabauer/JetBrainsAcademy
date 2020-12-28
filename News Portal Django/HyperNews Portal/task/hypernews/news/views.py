from django.shortcuts import render
from django.conf import settings
from django.views import View
from django.http import Http404
import json


with open(settings.NEWS_JSON_PATH, "r") as f:
    news_json = json.loads(f.read())
    news_json = sorted(news_json, key=lambda k: k.get('created', 0), reverse=True)


class MainView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request, 'news/index.html', context={
                'message': settings.MESSAGE
            }
        )

class NewsView(View):
    def get(self, request, news_link, *args, **kwargs):
        if news_link not in [x['link'] for x in news_json]:
            raise Http404
        news = ''
        for i in news_json:
            if i['link'] == news_link:
                news = i
        return render(
            request, 'news/news.html', context={
                'news': news
            }
        )

class MainNewsView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request, 'news/main_news.html', context={
                'news_batch': news_json
            }
        )

from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.http import Http404
import json, datetime, random


with open(settings.NEWS_JSON_PATH, "r") as f:
    news_json = sorted(json.loads(f.read()), key=lambda k: k.get('created', 0), reverse=True)


def assign_news_id(news_list):
    links = [x['link'] for x in news_json]
    while True:
        new_link = random.randint(1, 1000000000)
        if new_link not in links:
            return new_link


def add_new_news(title, body):
    news_json.append(
        {
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": body,
            "title": title,
            "link": assign_news_id(news_json)
        })
    with open(settings.NEWS_JSON_PATH, "w") as f:
        f.write(json.dumps(news_json))


class MainView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/news/')

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
        news_filter = request.GET.get('q')
        news_to_display = []
        if news_filter != None:
            for news in news_json:
                if news['title'] == news_filter:
                    news_to_display.append(news)
        else:
            news_to_display = news_json

        dates = sorted(list(set(
                        [
                            datetime.datetime.strptime(x['created'], '%Y-%m-%d %H:%M:%S').date()
                            for x in news_to_display
                        ]
                    )), reverse=True)
        dates = [str(x) for x in dates]

        return render(
            request, 'news/main_news.html', context={
                'news_batch': news_to_display,
                'dates': dates,
            }
        )

class CreateNewsView(View):
    def post(self, request, *args, **kwargs):
        title = request.POST.get('news_title')
        body = request.POST.get('news_body')
        add_new_news(title, body)
        return redirect('/news/create/')

    def get(self, request, *args, **kwargs):
        return render(
            request, 'news/create_news.html'
        )

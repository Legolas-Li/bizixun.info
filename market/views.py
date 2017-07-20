# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
import time
import sched
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from . import models
from lxml import etree
import requests
from django.db.models import Count, Min, Max, Sum

# Create your views here.
def get_index_html(request):
    return render(request, 'index.html')


def get_market_data(request):
    market_list = []
    symbol_list = models.Symbol.objects.all()
    for i in symbol_list:
        i_max = models.Market.objects.filter(symbol=i).filter(enabled=True).order_by('-price')[0]
        i_min = models.Market.objects.filter(symbol=i).filter(enabled=True).order_by('price')[0]
        market_json = {}
        market_json["symbol"] = i.name
        market_json["highest"] = i_max.price
        market_json["hPlatform"] = i_max.platform
        market_json["hHome"] = i_max.home

        market_json["lowest"] = i_min.price
        market_json["lPlatform"] = i_min.platform
        market_json["lHome"] = i_min.home
        points = round(i_max.price-i_min.price, 3)
        profits = round((points/i_min.price) * 100, 3)
        market_json["points"] = points
        market_json["profits"] = profits
        market_list.append(market_json)
    return JsonResponse({"data": market_list})

#def get_price(url):
#    result = requests.get(default_login_url)
#    return result.content


def get_price(url):
    result = requests.get(url)
    selector = etree.HTML(result.content)
    price = selector.xpath("/html/body/div[@id='container_outer']/div[@id='container']/div[@id='right_bar']/div[@id='sub_container']/div[@id='sub_component']/div[@id='sub_component_body']/div[@id='orderbook']/div[@id='price']")[0].text
    return price


def update():
    symbol_list = models.Symbol.objects.all()
    for i in symbol_list:
        symbol_list = models.Market.objects.filter(symbol=i)
        for i in symbol_list:
            price = get_price(i.url)
            i.price = price
            i.save()


#data=Data()
#data.update()

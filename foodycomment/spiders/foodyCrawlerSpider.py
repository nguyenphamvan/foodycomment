# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider
from foodycomment.items import FoodycommentItem
from scrapy_splash import SplashRequest

script1 = """
function main(splash)
    assert(splash:go(splash.args.url))
    count = 0
    while count < 50 do
        local get_dimensions = splash:jsfunc([[
            function () {
                e = document.getElementsByClassName('btn-load-more ng-scope ng-enter-prepare')[0]
                if (e) {
                    e = e.firstElementChild
                    var rect = e.getClientRects()[0];
                    return {"x": rect.left, "y": rect.top}
                } else {
                    return {"x": 0, "y": 0}
                }

            }
        ]])
        splash:set_viewport_full()
        splash:wait(0.1)
        local dimensions = get_dimensions()
        if dimensions.x==0 and dimensions.y==0 then 
            break
        else
            splash:mouse_click(dimensions.x, dimensions.y)
            splash:wait(0.1)
            count = count + 1
        end
    end
    return splash:html() 
end
"""

script2 = """
function main(splash)
    assert(splash:go(splash.args.url))
    count = 0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        while count < 10 do
        local get_dimensions = splash:jsfunc([[
            function () {
                e = document.getElementsByClassName('pn-loadmore fd-clearbox ng-scope')[0]
                if (e) {
                    e = e.firstElementChild
                    var rect = e.getClientRects()[0];
                    return {"x": rect.left, "y": rect.top}
                } else {
                    return {"x": 0, "y": 0}
                }
            }
        ]])
        splash:set_viewport_full()
        splash:wait(0.1)
        local dimensions = get_dimensions()
        if dimensions.x==0 and dimensions.y==0 then 
            break
        else
            splash:mouse_click(dimensions.x, dimensions.y)
            splash:wait(1)
            count = count + 1
        end
    end
    return splash:html() 
end
"""

script3 = """
function main(splash)
    splash:init_cookies(splash.args.cookies)
    local url = splash.args.url
    assert(splash:go(url))
    assert(splash:wait(0.5))
    return {
        cookies = splash:get_cookies(),
        html = splash:html()
    }
end
"""


class FoodycrawlerSpider(scrapy.Spider):
    name = 'foodycrawler'
    allowed_domains = ['foody.vn/ha-noi']
    start_urls = ['https://www.foody.vn/ha-noi/o-dau']

    MAX = 50000
    count = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': script1, 'wait': 2})


    def parse(self, response):
        urls = response.xpath('//div[@class="ldc-item-img"]/a/@href').extract()
        for url in urls:
            full_url = response.urljoin(url)
            yield Request(full_url, callback=self.parse_lua, dont_filter=True)

    def parse_lua(self, response):
        yield SplashRequest(response.url, self.parse_item, endpoint='execute', args={'lua_source': script2, 'wait': 0.5},
                            dont_filter=True)

    def parse_item(self, response):
        items = response.xpath('//ul[@class="review-list fd-clearbox ng-scope"]/li')
        print(len(items))
        for sel in items:
            rating = sel.xpath('.//div[@ng-mouseenter="ReviewRatingPopup()"]/span/text()').extract_first()
            review = sel.xpath('.//div[@ng-class="{\'toggle-height\':DesMore}"]/span/text()').extract_first().decode('utf-8')
            item = FoodycommentItem()
            item['rating'] = rating
            item['comment'] = review

            self.count += 1
            if self.count > self.MAX:
                raise CloseSpider('Crawled enough comments')
            yield item

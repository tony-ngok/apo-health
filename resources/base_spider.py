import scrapy
import random


class BaseSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)

    @classmethod
    def ssl(cls):
        ciphers = (
            "RSA+3DES:RSA+AES:RSA+AESGCM:ECDH+AESGCM:DH+AESGCM:ECDH+AES256"
            ":DH+AES256:ECDH+AES128:ECDH+HIGH:DH+HIGH:DH+3DES:RSA+HIGH:DH+AES:ECDH+3DES".split(":")
        )
        random.shuffle(ciphers)
        ciphers = ":".join(ciphers)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        return ciphers

    def parse_cookie_header(self, header):
        cookies = {}
        parts = header.split(";")
        for part in parts:
            if "=" in part:
                key, value = part.strip().split("=", 1)
                cookies[key] = value
        return cookies

    def get_cookies_from_response(self, response):
        cookies = {}
        set_cookie_headers = response.headers.getlist("Set-Cookie")
        for header in set_cookie_headers:
            cookie = self.parse_cookie_header(header.decode("utf-8"))
            cookies.update(cookie)
        return cookies

    def update_cookies(self, response):
        self.cookies = self.get_cookies_from_response(response)

    def write_html_response_for_debug(self, response):
        out_put_file = response.url + ".html"
        with open("tmp/" + out_put_file, "w", encoding="utf-8") as file:
            file.write(response.text)

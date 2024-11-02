from resources import settings

# Scrapy settings for apo_health project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "apo_health"

SPIDER_MODULES = ["apo_health.spiders"]
NEWSPIDER_MODULE = "apo_health.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "apo_health (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True
COOKIES_DEBUG = True


# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "apo_health.middlewares.apo_healthSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "apo_health.middlewares.apo_healthDownloaderMiddleware": 543,
# }

# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
# }
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

HTTPERROR_ALLOWED_CODES = [400, 404]

# https://docs.scrapy.org/en/2.11/topics/downloader-middleware.html?highlight=retry
RETRY_HTTP_CODES = [401, 403, 408, 429, 500, 502, 503, 504, 522, 524]
RETRY_TIMES = 10000

# DOWNLOAD_DELAY = 0.1

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

LOG_FILE = "apo_health.log"
LOG_LEVEL = "INFO"

# DOWNLOADER_CLIENT_TLS_CIPHERS = settings.DOWNLOADER_CLIENT_TLS_CIPHERS
# ELASTICSEARCH_SERVERS = settings.ELASTICSEARCH_SERVERS
# ELASTICSEARCH_USERNAME = settings.ELASTICSEARCH_USERNAME
# ELASTICSEARCH_PASSWORD = settings.ELASTICSEARCH_PASSWORD
# ELASTICSEARCH_TIMEOUT = settings.ELASTICSEARCH_TIMEOUT
# ELASTICSEARCH_MAX_RETRY = settings.ELASTICSEARCH_MAX_RETRY

# DOWNLOADER_MIDDLEWARES = {
#     "scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware": None,
#     "scrapy_random_ua.RandomUserAgentMiddleware": 400,
#     "scrapy_webshare.middleware.WebshareMiddleware": 500,
# }
# WEBSHARE_ENABLED = True
# WEBSHARE_USER = settings.WEBSHARE_USER
# WEBSHARE_PASSWORD = settings.WEBSHARE_PASSWORD
# WEBSHARE_COUNTRY = settings.WEBSHARE_COUNTRY

MONGO_URI = "mongodb://mongouser:XSzY1nHbxi@34.172.204.102:27017"
DAYS_BEF = 1

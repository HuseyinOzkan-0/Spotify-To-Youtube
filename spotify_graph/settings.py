BOT_NAME = 'spotify_graph'

SPIDER_MODULES = ['spotify_graph.spiders']
NEWSPIDER_MODULE = 'spotify_graph.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure item pipelines
ITEM_PIPELINES = {
   'spotify_graph.pipelines.FalkorDBPipeline': 300,
}

# User Agent to get Desktop view (hopefully)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

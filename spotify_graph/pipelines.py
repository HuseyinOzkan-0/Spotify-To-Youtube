from .orm import FalkorGraphORM

class FalkorDBPipeline:
    def __init__(self):
        self.orm = None

    def open_spider(self, spider):
        self.orm = FalkorGraphORM()

    def process_item(self, item, spider):
        # We assume the item is a Playlist dataclass or compatible object
        # The spider should yield a Playlist object
        print(f"Pipeline received playlist: {item.name}")
        self.orm.save_playlist(item)
        return item

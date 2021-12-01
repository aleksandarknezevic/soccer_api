from flask_smorest import Page


class CursorPage(Page):
    @property
    def item_count(self):
        return len(self.collection)

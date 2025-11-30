# server/storage.py
import itertools
from collections import defaultdict

class Storage:
    def __init__(self):
        self.groups = {}  # group -> list of article ids
        self.articles = {}  # id -> article dict
        self._id_iter = itertools.count(1)

    def add_group(self, name):
        if name not in self.groups:
            self.groups[name] = []

    def list_groups(self):
        return list(self.groups.keys())

    def has_group(self, name):
        return name in self.groups

    def add_article(self, group, subject, frm, body):
        if group not in self.groups:
            self.add_group(group)
        aid = next(self._id_iter)
        art = {"id": aid, "subject": subject, "from": frm, "body": body, "group": group}
        self.articles[aid] = art
        self.groups[group].append(aid)
        return aid

    def count_articles(self, group):
        return len(self.groups.get(group, []))

    def get_article(self, group, aid):
        if group is None:
            return None
        if aid in self.groups.get(group, []):
            return self.articles.get(aid)
        return None

    def get_article_any(self, aid):
        return self.articles.get(aid)

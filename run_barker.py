#!/Users/nathancheever/miniconda3/envs/barker/bin/python
# -*- coding:utf-8 -*-
"""Run a batch"""

from app.update_bookmarks import CollectUpdateBookmarks
from app.create_newsletter import NewsletterTemplate
from app.email_service import EmailService


if __name__ == '__main__':
    success = CollectUpdateBookmarks().main()
    if success:
        success = NewsletterTemplate().main()
        if success:
            EmailService().main()

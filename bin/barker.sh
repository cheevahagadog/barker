#!/usr/bin/env bash

# Collect and update the bookmark table
python -m app.get_bookmarks

# Create the HTML template
python -m app.create_newsletter

# Send email
python -m app.email_service

#!/usr/bin/env bash

# Activate your venv (here I use conda)
source activate barker

# Collect and update the bookmark table
python -m app.update_bookmarks

# Create the HTML template
python -m app.create_newsletter

# Send email
python -m app.email_service

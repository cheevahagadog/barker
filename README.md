Barker
======

A personal newsletter generator based on your Chrome bookmarks.

Motivation
----------
I follow a lot of great newsletters, read a lot of helpful blogs, and all around like to keep an organized bookmark library. But, no matter how organized I try to be, I quickly forget and find myself searching for resources I've already bookmarked.

As an attempt to remedy this first-world problem, I thought I'd create my own newsletter of resources I've bookmarked!

Setup
-----
```
$ git clone https://github.com/cheevahagadog/barker.git
```

Scripts were written using Python 3.6 and have not been tested for portability to Python 2.
I'd recommend creating a virtual environment
```
$ virtualenv venv
(OR w/ conda)
$ conda create -n venv python=3
```
Then activate
```
$ source venv/bin/activate
OR
$ source activate venv
```
Install necessary packages
```
$ pip install -r requirements.txt
```

Using Barker
------------
Once you've cloned the repo, setup the venv, and installed packages from the `requirements.txt`, Barker will need you to 
save your email address and password in a safe location (I saved it in my `~/.bash_profile` location). If you would like
to include your upcoming meetups on your newsletter, you will need to [create an API key](https://www.meetup.com/meetup_api/) 
(free) on meetup.com and export
it like the others. Once you have added them so they match the variable names in the `config.py` file, you can run
`source ~/.bash_profile`.

To run barker, you can either run it manually with `bash bin/barker.sh` or set it up on a cron job. Be sure to activate 
the venv you created before running!

TODO
-------------------
 - Currently, Barker works only with Chrome bookmarks and with a Gmail account. In the future, I would like to work on 
integrating other browsers and email providers.  
 - More complete testing suite.  
 - Bash script to take user input and set variables in `config.py`

Contributing
------------
1. Fork it (`https://github.com/cheevahagadog/barker.git`)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am "adding some feature"`)
4. Push to branch (`git push origin my-new-feature`)
5. Create new Pull Request

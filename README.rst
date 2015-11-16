README

HACKING
=======
So, I'm still messing with the best way to actually be able to work on this.

Two things that (currently) work:  
You can do python setup.py install, and get a functioning useage (as long as you're not in the same directory)

You an do python setup.py sdist, and then pip install the resulting tarball, and that works.

I have NOT managed to get pip install -e . to work.

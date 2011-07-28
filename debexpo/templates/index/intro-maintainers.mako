# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

${ c.custom_html }

Introduction for maintainers
Welcome to mentors.debian.net

We are glad that you found your way to our web site. Honestly the whole web site is just there to get your work into Debian. Your contribution is appreciated and it would be a pity if you didn't find a sponsor to upload your packages. Read on to see in what ways we will be helping you find a sponsor.
How will my package get into Debian?

This web site is a public package repository of source packages. You can upload your package to this server (through special tools like 'dupload' or 'dput') and after a few checks it will be stored in our repository. Interested sponsors can then download the package and upload it to Debian. So the basic procedure is:

    * Sign up for an account. Getting an account on this server is an automatic process and will just take a moment. We require registration so we have a valid email address where sponsors can reach you.
    * Upload your package to mentors.debian.net. You don't need to put your packages into any other web space on the internet. Everybody will be able to download your package using either the web browser, the 'dget' tools or even through a simple run of apt-get source ....
    * Your package is on display on the main page of mentors.debian.net so interested sponsors will see it and hopefully check it out.
    * You will be shown an RFS (request-for-sponsorship) template that you can send to the debian-mentors mailing list to draw attention to your package.
    * Finally a sponsor will hopefully pick up your package and upload it on your behalf. Bingo - your package is publicly available in Debian. And this server will automatically send you an email in case you did not notice the upload.

Is my package technically okay?

When you upload your package to mentors.debian.net it will automatically be checked for common mistakes. You will get an information email after the upload. Either your package contains bugs and will be rejected. Or the package is clean but we perhaps find minor technical issues. You will get hints about how to fix the package. If the email tells you that your package is fine then a sponsor will still do further checks. Don't worry too much. If your package is accepted by mentors.debian.net then let the sponsor help you with the rest.
The software I packaged is not yet available in Debian.

Please read this section of the Debian policy if the software you packaged is not yet in Debian. You need to follow a certain procedure to show other people you are working on the package.
How long will it take until my upload is available to sponsors?

Our automatic processes will check for newly incoming packages every 30 seconds. You will usually get a reply by email within a minute.
Will my name stay visible on the package?

Yes. The Debian project appreciates the work you do. So you will be named as the official maintainer of the package in Debian. You will even get the bug reports if people discover problems in your package. Besides from not being able to upload the package directly into Debian you are treated as a full member of the community. 

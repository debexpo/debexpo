# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>Package reviews</h1>

<p>You can help to review packages. That is possible even if you are not a Debian developer (<i>yet</i>). No reason to be shy, it is ok if you do not know everything or you are not entirely sure if your suggestions are correct. Any help is appreciated. Interested in diving in? It is easy:</p>

<h3>Why should I review packages? I can not upload them!</h3>

<p>Glad you ask! There are many reasons why you should review packages even if you can't actually upload them.</p>

<ul>
    <li>The person you are reviewing will appreciate it. Chances are, you find problems in a package the person was not aware of yet. So he can learn from you.</li>
    <li>Eventually the package you are reviewing will be in a very good shape and you happen to learn something yourself. Moreover, you will also learn about best practices and workflows other people are using. Even if the package does not meet Debian's quality standards you can learn how <i>not to do</i> things.</li>
    <li>People who <i>can</i> upload may decide based on your review whether the package in question is a suitable candidate or not.</li>
</ul>

<h3>How can I review packages?</h3>

<p>Pick a source package and start. There is no single correct way to review packages, but chances are you may want to have a look on the following things:</p>

<ul>
    <li>Verify Lintian outputs: Did Lintian miss something, are fixes semantically correct?</li>
    <li>Does the package satisfy <a href="http://www.debian.org/doc/manuals/developers-reference/best-pkging-practices.html">Debian's best practices</a> for packages?</li>
    <li>Does the package correctly declare dependencies as defined in the policy?</li>
    <li>Does the package meet the <a href="http://www.debian.org/social_contract">DFSG</a>? If yes, is the copyright file up to date and correct?</li>
    <li>Do the maintainer scripts supplied with the package look robust, idempotent and useful?</li>
    <li>Is there a watch file? If yes, does it work?</li>
    <li>Can you build the package in a clean build chroot?</li>
    <li>Was the upstream tarball modified? If yes, is there a good reason to do so?</li>
</ul>

<h3>Established sponsor guidelines</h3>

<p>Several Debian Developers published their personal sponsor guidelines. Those are rules applying for a particular person or a specific packaging team in case you want to have a package sponsored by them. Typically those rules extend the Debian policy by custom requirements, or require a particular workflow from you. You can have a look at some guidelines from different people on our ${ h.tags.link_to( _('sponsors side'), h.url('sponsors')) }</p>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <link rel="stylesheet" type="text/css" href="/style.css">
        <title>${ c.config['debexpo.sitename'] }</title>
% if c.feed_url:

    <link rel="alternate" href="${ c.feed_url }" title="RSS Feed" type="application/rss+xml" />

% endif

    </head>
    <body>
        <div id="header">
        <div id="upperheader">
            <div id="logo">
		${ h.tags.image( c.config['debexpo.logo'], c.config['debexpo.sitename'])}	
            </div><!-- end logo -->
	    <p class="section">${ c.config['debexpo.sitename'] }</p>
            <div id="searchbox">
	        <h2>${ c.config['debexpo.tagline'] }</h2>
            </div><!-- end searchbox -->
        </div><!-- end upperheader -->
        <div id="navbar">
            <ul>
		<li>${ h.tags.link_to(
                        _('Start page'),
                        h.url('index')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Package list'),
                        h.url('packages')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Maintainer'),
                        h.url('intro-maintainers')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Sponsors'),
                        h.url('intro-sponsors')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Reviews'),
                        h.url('intro-reviewers')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Q & A'),
                        h.url('qa')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Contact'),
                        h.url('contact')) }
                </li>
            </ul>
        </div><!-- end navbar -->
        <p id="breadcrumbs"> 
	% for cur_part in h.url.current().split("/"):
	${ cur_part  } /
	% endfor
	</p>
        </div><!-- end header -->
        <div id="content">
	    <span class="relatedpages">

                % if 'user_id' not in session:
                ${ h.tags.link_to(
                        _('Sign me up'),
                        h.url(controller='register', action='register')) }
                
                ${ h.tags.link_to(
                        _('Login'),
                        h.url('/login')) }
                
                % endif
                % if session.get('user_type') in (h.constants.USER_STATUS_MAINTAINER, h.constants.USER_STATUS_NORMAL):
                ${ h.tags.link_to(
                        _('My account'),
                        h.url('my')) }
                
                ${ h.tags.link_to(
                        _('My packages'),
                        h.url(controller='packages', action='my')) }
                % endif


	    </span>
		${next.body()}
	</div><!-- end content -->
        <div id="footer">
	<p>debexpo
	-
	<a href="mailto:${ c.config['debexpo.email'] }">Support contact</a>
	% if 'user_id' in session:
        -
        <a href="/logout">Logout</a>
        % endif
	</p>
        </div><!-- end footer -->
    </body>
</html>


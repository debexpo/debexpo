<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="${ h.url("/style.css") }" />
        <script src="${ h.url("/jquery-1.7.1.min.js") }" type="text/javascript"></script>
        <script src="${ h.url("/debexpo.js") }" type="text/javascript"></script>
        <title>${ c.config['debexpo.sitename'] }</title>
% if c.feed_url:

    <link rel="alternate" href="${ c.feed_url }" title="RSS Feed" type="application/rss+xml" />

% endif

    </head>
    <body>
        <div id="header">
        <div id="upperheader">
            <div id="logo">
		${ h.tags.link_to(  h.tags.image( c.config['debexpo.logo'], c.config['debexpo.sitename']) , 'http://www.debian.org') }
            </div><!-- end logo -->
	    <p class="section">${ h.tags.link_to( c.config['debexpo.sitetitle'], h.url('index')) }</p>
            <div id="searchbox">
	        ${ c.config['debexpo.tagline'] }
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
                        _('Reviews'),
                        h.url('intro-reviewers')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Sponsors'),
                        h.url('sponsors')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Q & A'),
                        h.url('qa')) }
                </li>

		<li>${ h.tags.link_to(
                        _('Contact'),
                        h.url('contact')) }
                </li>
		<li>${ h.tags.link_to(
                        _('Status'),
                        h.url('status')) }
                </li>
            </ul>
        </div><!-- end navbar -->
        <p id="breadcrumbs">
        <!--
	% for cur_part in h.url.current().split("/"):
	${ cur_part  } /
	% endfor
	-->
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
        % if c.submenu and c.submenu.has_menu():
            <%include file="submenu.mako" />
        % endif
		${next.body()}
	</div><!-- end content -->
        <div id="footer">
	<p>© 2008-2015 ${c.config['debexpo.sitename']}
	-
    Hosting and hardware provided by <a href="http://www.wavecon.de">Wavecon</a>
    -
    <a href="https://alioth.debian.org/projects/debexpo/">${ _('Source code and bugs')}</a>
    -
    <a href="https://github.com/debexpo/debexpo">${ _('GitHub if you prefer')}</a>
	-
    ${ h.tags.link_to( _('Contact'), h.url('contact')) }
	% if 'user_id' in session:
        -
        <a href="${ h.url("/logout") }">Logout</a>
    % endif
    % if c.feed_url:
    <a class="rss_logo" href="${ c.feed_url }">RSS</a>
    % endif
	</p>
        </div><!-- end footer -->
    </body>
</html>


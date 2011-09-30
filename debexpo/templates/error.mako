# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<div class="error-border">
% if c.code == 401:
    <h1>${ _('Error') } 401 - ${ _('Authentication required') }</h1>
    <p>
        ${ _('You need to be logged in to use this function.') }
    </p>
% elif c.code == 403:
    <h1>${ _('Error') } 403 - ${ _('Not authorized') }</h1>
    <p>
        ${ _('You do not have the permission to use this function.') }
    </p>
% elif c.code == 404:
    <h1>${ _('Error') } 404 - ${ _('Page not found') }</h1>
    <p>
        ${ _('The page you requested does not exist.') }
    </p>
% else:
    <h1>${ _('Internal error %s') % c.code }</h1>
    <p>
        ${ _('''An unexpected error occured in this application.
            The administrator will get a detailed report about the
            error situation. We appreciate if you give us more
            information how this error situation happened.''') }
    </p>
% endif

<p>
    ${ _('''If you have questions feel free to contact us
        at <a href="mailto:%s">%s</a>.'''
        % (config['debexpo.email'], config['debexpo.email'])) | n}
</p>
</div>

# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>To: ${ c.to }
Subject: Accepted ${ c.changes['Source'] } ${ c.changes['Version'] } (${ c.changes['Architecture'] })

${ c.changes_contents }

Accepted:
% for fileinfo in c.changes['Files']:
${ fileinfo['name'] }
  to ${ c.dest }/${ fileinfo['name'] }
% endfor

# -*- coding: utf-8 -*-
<%inherit file="/base.mako"/>

<h1>${ _('Worker job status') }</h1>

<table>
    <tr>
        <th>Job name</th>
        <th>Last run</th>
        <th>Interval</th>
        <th>Status</th>
    </tr>
    % for job in c.jobs:
    <tr class='qa'>
        <td>${ job['name'] }</td>
        <td>${ job['last_run'] }</td>
        <td>${ job['interval'] }</td>
        <td class='severity-${ job['status'] }'><span class='visibility'>${ job['message'] }</span></td>
    </tr>
    % endfor
</table>

<p>There are <span class='error-message'>${ c.pending_packages }</span> pending packages on queue.</p>

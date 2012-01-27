/*
 * debexpo.js – Javascript utility functions for the debexpo web interface
 *
 * This file is part of debexpo - http://debexpo.workaround.org
 *
 * Copyright © 2012 Nicolas Dandrimont <Nicolas.Dandrimont@crans.org>
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 */

function toggle_qa(header, speed) {
    vis = $(header).siblings(".visibility");
    if (vis.html() == "+") {
        vis.html("–");
    } else {
        if ($(header).siblings(".qa-content").size() > 0) {
            vis.html("+");
        }
    }
    if (!speed) {
        $(header).siblings(".qa-content").toggle();
    } else {
        $(header).siblings(".qa-content").toggle(speed);
    }
}

function expand_qa(header, speed) {
    vis = $(header).siblings(".visibility");
    if (vis.html() == "+") {
        toggle_qa(header, speed);
    }
}

function collapse_qa(header, speed) {
    vis = $(header).siblings(".visibility");
    if (vis.html() != "+") {
        toggle_qa(header, speed);
    }
}

$(document).ready(function() {

    $(".qa-header").click(function() {
        toggle_qa(this, "fast");
    });

    $(".severity-info .qa-header").each(function() {
        toggle_qa(this);
    });

    $(".qa-toplevel-header").after('<div class="qa-toggle">Toggle [<span class="qa-toggle-all">All</span>|<span class="qa-toggle-info">Info</span>]</div>')

    $(".qa-toggle-all").toggle(
        function() {
            $(this).parent().next(".qa").find(".qa-header").each(function() {
                expand_qa(this, "fast");
            })
                },
        function() {
            $(this).parent().next(".qa").find(".qa-header").each(function() {
                collapse_qa(this, "fast");
            })
                }
    );

    $(".qa-toggle-info").toggle(
        function() {
            $(this).parent().next(".qa").find(".severity-info .qa-header").each(function() {
                expand_qa(this, "fast");
            })
                },
        function() {
            $(this).parent().next(".qa").find(".severity-info .qa-header").each(function() {
                collapse_qa(this, "fast");
            })
                }
    );

});
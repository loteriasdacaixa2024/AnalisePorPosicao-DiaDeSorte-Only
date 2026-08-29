/* Prefixo público (Nginx /diadesorte). Localmente fica vazio. */
(function () {
    'use strict';

    var root = document.documentElement.getAttribute('data-app-root') || '';
    if (root === '/') {
        root = '';
    }
    window.APP_ROOT = root;

    var OTHER_APPS = [
        '/lotterylablive',
        '/centralmodalidades',
        '/centrallocaisdasorte',
        '/centralbolaodasorte',
        '/lotocheck',
        '/estrategias',
        '/jupyternotebook'
    ];

    function isOtherApp(pathname) {
        var i;
        if (pathname === '/app' || pathname.indexOf('/app/') === 0) {
            return true;
        }
        if (pathname === '/boloes' || pathname.indexOf('/boloes/') === 0) {
            return true;
        }
        for (i = 0; i < OTHER_APPS.length; i++) {
            if (pathname === OTHER_APPS[i] || pathname.indexOf(OTHER_APPS[i] + '/') === 0) {
                return true;
            }
        }
        return false;
    }

    function prefixPath(pathname, search, hash) {
        search = search || '';
        hash = hash || '';
        if (!pathname) {
            pathname = '/';
        }
        if (isOtherApp(pathname)) {
            return pathname + search + hash;
        }
        if (!root) {
            return pathname + search + hash;
        }
        if (pathname === root || pathname.indexOf(root + '/') === 0) {
            return pathname + search + hash;
        }
        if (pathname.charAt(0) !== '/') {
            return pathname + search + hash;
        }
        return root + pathname + search + hash;
    }

    function appUrl(path) {
        if (path == null || path === '') {
            return root ? root + '/' : '/';
        }
        if (typeof path !== 'string') {
            return path;
        }
        if (/^(mailto:|tel:|javascript:|data:|blob:|#)/i.test(path)) {
            return path;
        }
        if (path.indexOf('//') === 0) {
            return path;
        }
        if (/^https?:/i.test(path)) {
            try {
                var abs = new URL(path);
                if (abs.origin !== window.location.origin) {
                    return path;
                }
                return abs.origin + prefixPath(abs.pathname, abs.search, abs.hash);
            } catch (e) {
                return path;
            }
        }
        if (path.charAt(0) === '/') {
            try {
                var rel = new URL(path, window.location.origin);
                return prefixPath(rel.pathname, rel.search, rel.hash);
            } catch (e2) {
                return root + path;
            }
        }
        return path;
    }

    window.appUrl = appUrl;

    var origFetch = window.fetch;
    if (origFetch) {
        window.fetch = function (input, init) {
            try {
                if (typeof input === 'string') {
                    input = appUrl(input);
                } else if (typeof URL !== 'undefined' && input instanceof URL) {
                    input = new URL(appUrl(input.href));
                } else if (typeof Request !== 'undefined' && input instanceof Request) {
                    var next = appUrl(input.url);
                    if (next !== input.url) {
                        input = new Request(next, input);
                    }
                }
            } catch (err) { /* mantém a URL original */ }
            return origFetch.call(this, input, init);
        };
    }

    var origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function () {
        var args = Array.prototype.slice.call(arguments);
        if (typeof args[1] === 'string') {
            args[1] = appUrl(args[1]);
        }
        return origOpen.apply(this, args);
    };

    function prefixEl(el) {
        if (!el || !el.getAttribute) {
            return;
        }
        ['href', 'src', 'action'].forEach(function (attr) {
            if (!el.hasAttribute(attr)) {
                return;
            }
            var val = el.getAttribute(attr);
            if (!val) {
                return;
            }
            var prefixed = appUrl(val);
            if (prefixed !== val) {
                el.setAttribute(attr, prefixed);
            }
        });
    }

    function prefixTree(node) {
        if (!node) {
            return;
        }
        if (node.nodeType === 1) {
            prefixEl(node);
        }
        if (!node.querySelectorAll) {
            return;
        }
        node.querySelectorAll(
            'a[href], link[href], script[src], img[src], form[action], iframe[src], source[src], video[src], audio[src]'
        ).forEach(prefixEl);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            prefixTree(document);
        });
    } else {
        prefixTree(document);
    }

    if (typeof MutationObserver !== 'undefined') {
        new MutationObserver(function (mutations) {
            mutations.forEach(function (m) {
                m.addedNodes.forEach(function (node) {
                    if (node.nodeType === 1) {
                        prefixTree(node);
                    }
                });
            });
        }).observe(document.documentElement, { childList: true, subtree: true });
    }
})();

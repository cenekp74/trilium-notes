(function () {
    'use strict';

    // ---- Dark mode ----
    function getCookie(name) {
        var m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return m ? m[2] : null;
    }

    function setCookie(name, value, days) {
        var d = new Date();
        d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
        document.cookie = name + '=' + value + '; expires=' + d.toUTCString() + '; path=/; SameSite=Lax';
    }

    var toggleCb = document.getElementById('theme-toggle-cb');
    if (toggleCb) {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        toggleCb.checked = isDark;

        toggleCb.addEventListener('change', function () {
            var dark = this.checked;
            document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
            setCookie('theme', dark ? 'dark' : 'light', 365);
        });
    }

    var sidebar = document.getElementById('sidebar');
    var hamburger = document.getElementById('hamburger-btn');
    var backdrop = document.getElementById('sidebar-backdrop');
    var closeBtn = document.getElementById('sidebar-close');

    // ---- Mobile sidebar ----
    function openSidebar() {
        sidebar.classList.add('open');
        backdrop.classList.add('visible');
        hamburger.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        backdrop.classList.remove('visible');
        hamburger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    if (hamburger) hamburger.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (backdrop) backdrop.addEventListener('click', closeSidebar);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // ---- Tree: folder collapse/expand ----
    document.querySelectorAll('.tree-toggle').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var li = btn.closest('.tree-item');
            if (li) li.classList.toggle('collapsed');
        });
    });

    document.querySelectorAll('.tree-item.tree-dir > .tree-label').forEach(function (label) {
        label.addEventListener('click', function (e) {
            if (e.target.closest('.tree-toggle')) return;
            e.preventDefault();
            var li = label.closest('.tree-item');
            if (li) li.classList.toggle('collapsed');
        });
    });

    // ---- Expand path to active note and scroll into view ----
    function expandActiveNote() {
        var activeLink = document.querySelector('.sidebar-nav a.active');
        if (!activeLink) return;

        var node = activeLink.closest('.tree-item');
        while (node) {
            node.classList.remove('collapsed');
            var parentList = node.parentElement;
            if (!parentList) break;
            var parentItem = parentList.closest('.tree-item');
            if (!parentItem) break;
            node = parentItem;
        }

        setTimeout(function () {
            activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }, 80);
    }

    expandActiveNote();

    // ---- Live tree filter ----
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            filterTree(this.value.trim().toLowerCase());
        });
    }

    function filterTree(q) {
        var allItems = document.querySelectorAll('.sidebar-nav .tree-item');
        if (!q) {
            allItems.forEach(function (item) {
                item.style.display = '';
            });
            expandActiveNote();
            return;
        }

        allItems.forEach(function (item) { item.style.display = 'none'; });

        document.querySelectorAll('.sidebar-nav .tree-label a, .sidebar-nav .tree-label .tree-no-link')
            .forEach(function (el) {
                if (el.textContent.trim().toLowerCase().includes(q)) {
                    showWithAncestors(el.closest('.tree-item'));
                }
            });
    }

    function showWithAncestors(li) {
        if (!li) return;
        li.style.display = '';
        li.classList.remove('collapsed');
        var parent = li.parentElement;
        while (parent) {
            if (parent.classList && parent.classList.contains('tree-item')) {
                parent.style.display = '';
                parent.classList.remove('collapsed');
            }
            parent = parent.parentElement;
            if (parent && parent.id === 'sidebar') break;
        }
    }
})();

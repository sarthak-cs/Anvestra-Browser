from PyQt6.QtWidgets import QTabWidget, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineProfile

from history_manager import HistoryManager
import os

class TabManager(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.history_manager = HistoryManager()
        self.downloads = []
        
        self.add_new_tab()
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.handle_download)

    def add_new_tab(self, qurl=None):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)

        index = self.addTab(browser, "New Tab")
        self.setCurrentIndex(index)

        browser.titleChanged.connect(
            lambda title, browser=browser:
            self.setTabText(self.indexOf(browser), title)
        )

        browser.loadFinished.connect(
            lambda ok, browser=browser:
            self.record_history(browser, ok)
        )

        # browser.page().profile().downloadRequested.connect(self.handle_download)

        return browser

    def close_tab(self, index):
        if self.count() < 2:
            return
        self.removeTab(index)

    def current_browser(self):
        return self.currentWidget()
    
            
    def record_history(self, browser, ok):
        if ok:
            url = browser.url().toString()

            if url.startswith("http"):
                title = browser.page().title()
                self.history_manager.add_entry(title, url)

    def handle_download(self, download):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            download.downloadFileName()
        )

        if path:
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            download.accept()

            self.downloads.append({
                "filename": os.path.basename(path),
                "path": path
            })

    def open_internal_page(self, page_name):
        browser = self.add_new_tab(QUrl("about:blank"))

        if page_name == "history":
            browser.setHtml(
                self.get_history_html(),
                QUrl("https://Anvestra.local/history")
            )

        if page_name == "downloads":
            browser.setHtml(
                self.get_downloads_html(),
                QUrl("https://Anvestra.local/downloads")
            )
        if page_name == "about":
            browser.setHtml(
                self.get_about_html(),
                QUrl("https://Anvestra.local/about")
            )
        if page_name == "bookmarks":
            browser.setHtml(
                self.show_bookmarks(),
                QUrl("https://Anvestra.local/bookmarks")
            )
            
    def get_history_html(self):
        history = self.history_manager.get_history()

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial; padding: 20px; background: #111; color: white; }
                h1 { color: #00d4ff; }
                a { color: #00ff99; text-decoration: none; }
                .entry { margin-bottom: 10px; }
                .time { font-size: 12px; color: #aaa; }
            </style>
        </head>
        <body>
            <h1>Anvestra History</h1>
        """

        for title, url, timestamp in history:
            html += f"""
            <div class="entry">
                <a href="{url}">{title}</a>
                <div class="time">{timestamp}</div>
            </div>
            """

        html += "</body></html>"
        return html


    def show_bookmarks(self):
        bookmarks = self.history_manager.get_bookmarks()

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial; padding: 20px; background: #111; color: white; }
                h1 { color: #ff8800; }
                a { color: #00ff99; text-decoration: none; }
                .entry { margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <h1>Anvestra Bookmarks</h1>
            <ul>
        """
        for title, url in bookmarks:
            html += f'<li><a href="{url}">{title}</a></li>'
        html += "</ul></body></html>"
        return html
    

    def get_downloads_html(self):
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial; padding: 20px; background: #111; color: white; }
                h1 { color: #ff8800; }
                .entry { margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <h1>Anvestra Downloads</h1>
        """

        for item in self.downloads:
            html += f"""
            <div class="entry">
                {item['filename']} <br>
                <small>{item['path']}</small>
            </div>
            """

        html += "</body></html>"
        return html

    def get_about_html(self):
        return """
        <html>
            <head>
                <title>About Anvestra Browser</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background: linear-gradient(135deg, #0f172a, #1e293b);
                        color: #e2e8f0;
                        margin: 0;
                        padding: 0;
                    }

                    .container {
                        max-width: 950px;
                        margin: auto;
                        padding: 60px 30px;
                    }

                    .header {
                        text-align: center;
                        margin-bottom: 40px;
                    }

                    .logo {
                        width: 110px;
                        border-radius: 20%;
                        margin-bottom: 15px;
                        border: 2px solid #334155;
                    }

                    h1 {
                        font-size: 48px;
                        color: #38bdf8;
                        margin: 10px 0;
                    }

                    .tagline {
                        font-size: 16px;
                        opacity: 0.7;
                        margin-bottom: 10px;
                    }

                    .version {
                        font-size: 14px;
                        opacity: 0.5;
                    }

                    .card {
                        background: rgba(30, 41, 59, 0.6);
                        border: 1px solid #334155;
                        border-radius: 12px;
                        padding: 25px;
                        margin-top: 25px;
                    }

                    .card h2 {
                        color: #22c55e;
                        margin-bottom: 10px;
                    }

                    .card p {
                        line-height: 1.7;
                    }

                    ul {
                        margin-top: 10px;
                        padding-left: 20px;
                        line-height: 1.8;
                    }

                    .highlight {
                        color: #38bdf8;
                    }

                    a {
                        color: #38bdf8;
                        text-decoration: none;
                    }

                    a:hover {
                        text-decoration: underline;
                    }

                    .footer {
                        text-align: center;
                        margin-top: 50px;
                        font-size: 13px;
                        opacity: 0.5;
                    }
                </style>
            </head>

            <body>
                <div class="container">

                    <div class="header">
                        <img src="https://sarthak-cs.github.io/images/ST.webp" class="logo"/>
                        <h1>Anvestra Browser</h1>
                        <div class="tagline">A modular desktop browser built for systems-level exploration</div>
                        <div class="version">Version 0.1.0</div>
                    </div>

                    <div class="card">
                        <h2>Overview</h2>
                        <p>
                            Anvestra Browser is an experimental desktop web browser built using 
                            <span class="highlight">PyQt6</span> and 
                            <span class="highlight">Qt WebEngine (Chromium-based)</span>.
                        </p>
                        <p>
                            The project focuses on understanding browser internals such as tab lifecycle management,
                            input routing, history persistence and network-driven features, while maintaining a clean,
                            modular architecture.
                        </p>
                    </div>

                    <div class="card">
                        <h2>Core Features</h2>
                        <ul>
                            <li>Multi-tab browsing with dynamic tab lifecycle management</li>
                            <li>Configurable multi-search engine routing (Google, DuckDuckGo, Bing)</li>
                            <li>Real-time autocomplete (API + local history integration)</li>
                            <li>Persistent browsing history and internal system pages</li>
                            <li>Download management system</li>
                        </ul>
                    </div>

                    <div class="card">
                        <h2>Technical Stack</h2>
                        <ul>
                            <li>Python 3.13</li>
                            <li>PyQt6 (UI Layer)</li>
                            <li>Qt WebEngine (Rendering Engine)</li>
                            <li>SQLite / Local Storage for persistence</li>
                            <li>QNetworkAccessManager for async networking</li>
                        </ul>
                    </div>

                    <div class="card">
                        <h2>Purpose</h2>
                        <p>
                            This project was built as a systems-oriented learning exercise to explore how modern
                            browsers integrate UI, rendering engines, networking and local storage into a cohesive system.
                        </p>
                    </div>

                    <div class="card">
                        <h2>Developer</h2>
                        <p>
                            Built by <strong>Sarthak Tyagi</strong>
                        </p>
                        <p>
                            <a href="https://github.com/sarthak-cs">GitHub</a> |
                            <a href="https://www.linkedin.com/in/sarthak-tyagi-cs">LinkedIn</a> |
                            <a href="https://sarthak-cs.github.io">Portfolio</a>
                        </p>
                    </div>

                    <div class="footer">
                        © 2026 Anvestra Browser - Experimental Systems Project
                    </div>

                </div>
            </body>
            </html>
        """
    
    def closeEvent(self, event):
        self.history_manager.close()
        super().closeEvent(event)

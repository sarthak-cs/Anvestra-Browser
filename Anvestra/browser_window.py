import os
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QStyle, QToolBar, QLineEdit, QComboBox, QCompleter
)
from PyQt6.QtGui import QAction, QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import QSize, QUrl, QStringListModel, Qt, QTimer
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import json
from tab_manager import TabManager
from utils import build_url_from_input, SEARCH_ENGINES, DEFAULT_ENGINE
from history_manager import HistoryManager

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Anvestra Browser")
        self.setWindowIcon(QIcon("images/favicon.ico"))
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = TabManager()
        self.setCentralWidget(self.tabs)

        navbar = QToolBar()
        self.addToolBar(navbar)
        navbar.setIconSize(QSize(32, 32))
        
        self.history_manager = HistoryManager()

        back_btn = back_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "", self)
        back_btn.triggered.connect(lambda: self.tabs.current_browser().back())
        navbar.addAction(back_btn)

        forward_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "", self)
        forward_btn.triggered.connect(lambda: self.tabs.current_browser().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "", self)
        reload_btn.triggered.connect(lambda: self.tabs.current_browser().reload())
        navbar.addAction(reload_btn)

        stop_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "", self)
        stop_btn.triggered.connect(lambda: self.tabs.current_browser().stop())
        navbar.addAction(stop_btn)

        self.search_engine_selector = QComboBox()
        self.search_engine_selector.addItems(list(SEARCH_ENGINES.keys()))
        navbar.addWidget(self.search_engine_selector)

        self.search_engine_selector.setStyleSheet("""
            QComboBox {
                padding: 6px;
                font-size: 14px;
                background: #334155;
                color: white;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #555;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #334155;
            }
        """)

        self.search_engine_selector.setFixedWidth(120) 
        self.search_engine_selector.currentTextChanged.connect(self.switch_homepage)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.bookmark_btn = QPushButton("⭐")
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        navbar.addWidget(self.bookmark_btn)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        new_tab_btn = QAction("➕", self)
        # new_tab_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "", self)
        new_tab_btn.triggered.connect(lambda: self.tabs.add_new_tab())
        navbar.addAction(new_tab_btn)

        self.network_manager = QNetworkAccessManager()
        self.current_reply = None


        self.completer_model = QStringListModel()


        self.completer = QCompleter(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)

        self.url_bar.setCompleter(self.completer)

        self.completer.popup().setStyleSheet("""
            QListView {
                height: auto;
                background: #1e293b;
                color: white;
                font-size: 14px;
                padding: 4px;
                border: 1px solid #334155;
            }
            QListView::item:selected {
                background: #2563eb;
            }
        """)


        self.debounce_timer = QTimer()
        self.debounce_timer.setInterval(400)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.perform_suggest)

        self.current_query = ""

        self.url_bar.textEdited.connect(self.on_text_edited)

        QShortcut(QKeySequence("Ctrl+T"), self,
                  activated=lambda: self.tabs.add_new_tab())
        
        QShortcut(QKeySequence("Ctrl+R"), self,
                  activated=lambda: self.tabs.current_browser().reload())
        
        QShortcut(QKeySequence("Alt+Left"), self,
                  activated=lambda: self.tabs.current_browser().back())
        
        QShortcut(QKeySequence("Alt+Right"), self,
                  activated=lambda: self.tabs.current_browser().forward())

        QShortcut(QKeySequence("Ctrl+W"), self,
                  activated=lambda: self.tabs.close_tab(self.tabs.currentIndex()))

        QShortcut(QKeySequence("Ctrl+L"), self,
                  activated=self.focus_url_bar)
        QShortcut(QKeySequence("Ctrl+H"), self,
          activated=lambda: self.tabs.open_internal_page("history"))

        QShortcut(QKeySequence("Ctrl+D"), self,
                activated=lambda: self.tabs.open_internal_page("downloads"))
        
        history_btn = QAction("History", self)
        history_btn.triggered.connect(lambda: self.tabs.open_internal_page("history"))
        navbar.addAction(history_btn)
        downloads_btn = QAction("Downloads", self)
        downloads_btn.triggered.connect(lambda: self.tabs.open_internal_page("downloads"))
        navbar.addAction(downloads_btn)
        bookmarks_btn = QAction("Bookmarks", self)
        bookmarks_btn.triggered.connect(lambda: self.tabs.open_internal_page("bookmarks"))
        navbar.addAction(bookmarks_btn)
        about_btn = QAction("About", self)
        about_btn.triggered.connect(lambda: self.tabs.open_internal_page("about"))
        navbar.addAction(about_btn)
        
        QShortcut(QKeySequence("Ctrl+I"), self,
          activated=lambda: self.tabs.open_internal_page("about"))

        self.tabs.currentChanged.connect(self.update_urlbar_from_tab)


    def focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()


    def navigate_to_url(self):
        engine_name = self.search_engine_selector.currentText()
        qurl = build_url_from_input(self.url_bar.text(), engine_name)
        self.tabs.current_browser().setUrl(qurl)


    def update_urlbar(self, qurl):
        self.url_bar.setText(qurl.toString())


    def update_urlbar_from_tab(self, index):
        browser = self.tabs.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def switch_homepage(self, engine_name):
        browser = self.tabs.current_browser()
        if browser:
            browser.setUrl(build_url_from_input("", engine_name))


    def handle_suggest_reply(self, history_results, reply):
        if reply != self.current_reply:
            reply.deleteLater()
            return

        try:
            data = reply.readAll().data()
            suggestions = json.loads(data.decode())[1][:5]
        except:
            suggestions = []

        reply.deleteLater()
        self.current_reply = None

        combined = list(dict.fromkeys(history_results + suggestions))[:5]
        self.completer_model.setStringList(combined)

    def toggle_bookmark(self):
        browser = self.tabs.current_browser()
        if not browser:
            return

        url = browser.url().toString()
        title = browser.page().title()

        if self.history_manager.is_bookmarked(url):
            self.history_manager.remove_bookmark(url)
        else:
            self.history_manager.add_bookmark(title, url)

        self.update_bookmark_icon(url)

    def update_bookmark_icon(self, url):
        if self.history_manager.is_bookmarked(url):
            self.bookmark_btn.setText("★")
        else:
            self.bookmark_btn.setText("☆")

    def show_bookmarks(self):
        bookmarks = self.history_manager.get_bookmarks()

        html = "<h1>Bookmarks</h1><ul>"
        for title, url in bookmarks:
            html += f'<li><a href="{url}">{title or url}</a></li>'
        html += "</ul>"

        self.tabs.current_browser().setHtml(html)

    def on_tab_changed(self, index):
        browser = self.tabs.current_browser()
        if browser:
            self.update_bookmark_icon(browser.url().toString())


    def on_text_edited(self, text):
        self.current_query = text
        self.debounce_timer.start()
    
    def perform_suggest(self):
        text = self.current_query.strip()

        if len(text) < 2:
            self.completer_model.setStringList([])
            return

        browser = self.tabs.current_browser()
        if browser and browser.url().toString().startswith("https://Anvestra.local"):
            return

        if self.current_reply:
            self.current_reply.abort()
            self.current_reply.deleteLater()

        history_results = self.tabs.history_manager.search_urls(text)

        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={text}"
        request = QNetworkRequest(QUrl(url))

        reply = self.network_manager.get(request)
        self.current_reply = reply

        reply.finished.connect(
            lambda r=reply, h=history_results: self.handle_suggest_reply(h, r)
        )
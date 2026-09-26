import os

def create_files():
    # Define the files and their content
    files = {
        'index.html': '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Reader</title>
    <link rel="icon" type="image/svg+xml" href="Icon.svg">
    <!-- استدعاء خط Cairo -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Amiri&family=Cairo:wght@400;700&family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>

    <div id="sidebar">
        <div class="sidebar-content">
            <h2 data-i18n="sidebar_title">الملفات</h2>
            <ul id="file-list"></ul>
        </div>
    </div>

    <div id="main-content">
        <div id="toolbar">
            <div class="toolbar-right">
                <button id="toggle-btn" data-i18n="toggle_btn">☰ القائمة الجانبية</button>
            </div>
            <div class="toolbar-center">
                <span id="current-filename" data-i18n="placeholder_filename">الرجاء اختيار ملف</span>
            </div>
            <div class="toolbar-left">
                <button id="lang-btn">EN</button>
                <button id="theme-btn" data-i18n="theme_btn">🌙 الوضع الداكن</button>
                <button id="clear-data-btn" data-i18n="clear_data">مسح البيانات</button>
            </div>
        </div>
        <div id="viewer">
            <div class="placeholder" data-i18n="viewer_placeholder">الرجاء اختيار ملف نصي من القائمة الجانبية لعرض محتواه.<br>(استخدم الأسهم ← → للتنقل بين الملفات)</div>
        </div>
    </div>

    <div id="bottom-bar">
        <button id="prev-btn" data-i18n="prev_btn"> → السابق</button>
        <button id="font-down-btn">-</button>
        <span id="font-size-display">1.3</span>
        <button id="font-up-btn">+</button>
        <button id="font-family-btn" data-i18n="font_btn">خط</button>
        <button id="next-btn" data-i18n="next_btn">التالي ←</button>
    </div>

    <div id="sidebar-overlay"></div>
    <div id="toast" class="toast"></div>

    <script src="script.js" defer></script>
</body>
</html>''',

        'script.js': '''const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const toggleBtn = document.getElementById('toggle-btn');
const themeBtn = document.getElementById('theme-btn');
const fontUpBtn = document.getElementById('font-up-btn');
const fontDownBtn = document.getElementById('font-down-btn');
const fontSizeDisplay = document.getElementById('font-size-display');
const fontFamilyBtn = document.getElementById('font-family-btn');
const fileList = document.getElementById('file-list');
const viewer = document.getElementById('viewer');
const currentFilename = document.getElementById('current-filename');

// Array to keep track of all discovered files for navigation
let availableFiles = [];

const translations = {
    ar: {
        sidebar_title: 'الملفات',
        toggle_btn: '☰ القائمة الجانبية',
        placeholder_filename: 'الرجاء اختيار ملف',
        viewer_placeholder: 'الرجاء اختيار ملف نصي من القائمة الجانبية لعرض محتواه.<br>(استخدم الأسهم ← → للتنقل بين الملفات)',
        prev_btn: ' → السابق',
        next_btn: 'التالي ←',
        theme_light: '☀️ الوضع الفاتح',
        theme_dark: '🌙 الوضع الداكن',
        file_error: 'خطأ في تحميل الملف: ',
        font_btn: 'خط',
        font_changed: 'الخط الحالي: ',
        clear_data: 'مسح البيانات'
    },
    en: {
        sidebar_title: 'Files',
        toggle_btn: '☰ Sidebar',
        placeholder_filename: 'Please select a file',
        viewer_placeholder: 'Please select a text file from the sidebar to view its content.<br>(Use ← → arrows to navigate)',
        prev_btn: '← Previous',
        next_btn: 'Next →',
        theme_light: '☀️ Light Mode',
        theme_dark: '🌙 Dark Mode',
        file_error: 'Error loading file: ',
        font_btn: 'Font',
        font_changed: 'Current Font: ',
        clear_data: 'Clear Data'
    }
};

function setLanguage(lang, animate = false) {
    if (animate) {
        const targets = [sidebar, document.getElementById('main-content')];
        targets.forEach(t => t.classList.add('lang-transition'));

        setTimeout(() => {
            applyTranslations(lang);
            targets.forEach(t => t.classList.remove('lang-transition'));
        }, 150);
    } else {
        applyTranslations(lang);
    }
}

function applyTranslations(lang) {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            if (el.tagName === 'DIV' || el.tagName === 'SPAN') {
                el.innerHTML = translations[lang][key];
            } else {
                el.textContent = translations[lang][key];
            }
        }
    });

    // Restore filename if a file was already open
    const lastFile = localStorage.getItem('lastViewedFile');
    if (lastFile) {
        currentFilename.textContent = lastFile.replace('.txt', '');
    }

    localStorage.setItem('language', lang);
    document.getElementById('lang-btn').textContent = lang === 'ar' ? 'EN' : 'AR';

    // Update theme button text immediately when language changes
    updateThemeButtonText(localStorage.getItem('theme') || 'light');
}

// Cache settings
const CACHE_PREFIX = 'file_cache_';
const META_PREFIX = 'file_meta_';


function getCache(filename) {
    return localStorage.getItem(CACHE_PREFIX + filename);
}

function getMeta(filename) {
    return localStorage.getItem(META_PREFIX + filename);
}

function setCache(filename, content) {
    try {
        localStorage.setItem(CACHE_PREFIX + filename, content);
    } catch (e) {
        if (e.name === 'QuotaExceededError') {
            console.warn('Cache quota exceeded, some files may not be cached.');
        }
    }
}

function setMeta(filename, date) {
    localStorage.setItem(META_PREFIX + filename, date);
}

function removeCache(filename) {
    localStorage.removeItem(CACHE_PREFIX + filename);
    localStorage.removeItem(META_PREFIX + filename);
}

function clearInvalidCache(availableFiles) {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        if (key.startsWith(CACHE_PREFIX)) {
            const filename = key.substring(CACHE_PREFIX.length);
            if (!availableFiles.includes(filename)) {
                localStorage.removeItem(key);
            }
        }
    });
}

async function preFetchFiles(files) {
    for (const filename of files) {
        if (!getCache(filename)) {
            try {
                const response = await fetch(filename);
                if (response.ok) {
                    const text = await response.text();
                    setCache(filename, text);
                }
            } catch (e) {
                // Ignore pre-fetch errors
            }
        }
    }
}

// إدارة الثيم
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeButtonText(currentTheme);

// إدارة اللغة
const currentLang = localStorage.getItem('language') || 'ar';
setLanguage(currentLang);

// إدارة حجم الخط
let currentFontSize = parseFloat(localStorage.getItem('fontSize')) || 1.3;

const fonts = [
    { en: 'Cairo', ar: 'كايرو' },
    { en: 'Amiri', ar: 'أميري' },
    { en: 'Tajawal', ar: 'تجوال' }
];
let currentFontIndex = parseInt(localStorage.getItem('fontIndex')) || 0;

function updateFontSize() {
    viewer.style.fontSize = `${currentFontSize}rem`;
    localStorage.setItem('fontSize', currentFontSize);
    fontSizeDisplay.textContent = currentFontSize.toFixed(1);
}
updateFontSize();

function updateFontFamily() {
    const fontObj = fonts[currentFontIndex];
    const fontEn = fontObj.en;
    const fontAr = fontObj.ar;
    const lang = localStorage.getItem('language') || 'ar';

    document.documentElement.style.setProperty('--viewer-font', `'${fontEn}', sans-serif`);
    localStorage.setItem('fontIndex', currentFontIndex);

    const fontDisplayName = lang === 'ar' ? fontAr : fontEn;
    showToast(`${translations[lang].font_changed} ${fontDisplayName}`);
}
updateFontFamily();

fontUpBtn.addEventListener('click', () => {
    currentFontSize += 0.1;
    updateFontSize();
});

fontDownBtn.addEventListener('click', () => {
    if (currentFontSize > 0.5) {
        currentFontSize -= 0.1;
        updateFontSize();
    }
});

fontFamilyBtn.addEventListener('click', () => {
    currentFontIndex = (currentFontIndex + 1) % fonts.length;
    updateFontFamily();
});

themeBtn.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    let newTheme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButtonText(newTheme);
});

function updateThemeButtonText(theme) {
    const lang = localStorage.getItem('language') || 'ar';
    themeBtn.textContent = theme === 'dark' ? translations[lang].theme_light : translations[lang].theme_dark;
}

document.getElementById('clear-data-btn').addEventListener('click', () => {
    if (confirm('هل أنت متأكد من أنك تريد مسح جميع البيانات والإعدادات؟\\nAre you sure you want to clear all data and settings?')) {
        localStorage.clear();
        location.reload();
    }
});

toggleBtn.addEventListener('click', () => {
    toggleSidebar();
});

function toggleSidebar() {
    sidebar.classList.toggle('hidden');
    if (sidebarOverlay) {
        sidebarOverlay.classList.toggle('active');
    }
    localStorage.setItem('sidebarHidden', sidebar.classList.contains('hidden'));
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
        toggleSidebar();
    });
}

// Initialize sidebar state
if (localStorage.getItem('sidebarHidden') === 'true') {
    sidebar.classList.add('hidden');
}

document.getElementById('lang-btn').addEventListener('click', () => {
    const current = localStorage.getItem('language') || 'ar';
    const next = current === 'ar' ? 'en' : 'ar';
    setLanguage(next, true);
});

const prevBtn = document.getElementById('next-btn');
const nextBtn = document.getElementById('prev-btn');
prevBtn.addEventListener('click', () => navigateFile('prev'));
nextBtn.addEventListener('click', () => navigateFile('next'));

async function loadFileContent(filename) {
    if (!filename) return;

    // Auto-hide sidebar on mobile when a file is selected
    if (window.innerWidth <= 768 && !sidebar.classList.contains('hidden')) {
        toggleSidebar();
    }

    try {
        let text;
        const cachedContent = getCache(filename);
        const cachedMeta = getMeta(filename);

        // Check for changes using HEAD request
        const response = await fetch(filename, { method: 'HEAD' });
        const lastModified = response.headers.get('Last-Modified');
        const contentLength = response.headers.get('Content-Length');
        const metaString = `${lastModified}-${contentLength}`;

        if (cachedContent !== null && cachedMeta === metaString) {
            text = cachedContent;
        } else {
            const contentResponse = await fetch(filename);
            if (!contentResponse.ok) throw new Error('الملف غير موجود');
            text = await contentResponse.text();
            setCache(filename, text);
            setMeta(filename, metaString);
        }

        // Trigger viewer animation
        viewer.classList.remove('viewer-animating');
        void viewer.offsetWidth; // Force reflow to restart animation
        viewer.classList.add('viewer-animating');

        viewer.textContent = text + '\\n\\n\\n\\n\\n';
        viewer.scrollTop = 0;
        currentFilename.textContent = filename.replace('.txt', '');

        localStorage.setItem('lastViewedFile', filename);

        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-filename') === filename);
        });
    } catch (err) {
        viewer.innerHTML = `<span style="color:red">${translations[localStorage.getItem('language') || 'ar'].file_error}${err.message}</span>`;
    }
}

// Navigation Logic
function navigateFile(direction) {
    const currentFile = localStorage.getItem('lastViewedFile');
    const currentIndex = availableFiles.indexOf(currentFile);

    if (currentIndex === -1) return; // No file currently selected

    if (direction === 'next' && currentIndex < availableFiles.length - 1) {
        loadFileContent(availableFiles[currentIndex + 1]);
    } else if (direction === 'prev' && currentIndex > 0) {
        loadFileContent(availableFiles[currentIndex - 1]);
    }
}

// Keyboard Listeners
window.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        toggleSidebar();
    } else if (e.key === '=' || e.key === '+') {
        currentFontSize += 0.1;
        updateFontSize();
    } else if (e.key === '-' || e.key === '_') {
        if (currentFontSize > 0.5) {
            currentFontSize -= 0.1;
            updateFontSize();
        }
    } else if (e.key === 'ArrowRight') {
        // In RTL (Arabic), Right is "Prev" (index increases). In LTR (English), Right is "Next" (index increases).
        // The navigateFile function now uses 'next' for index+1 and 'prev' for index-1.
        const lang = localStorage.getItem('language') || 'ar';
        if (lang === 'ar') {
            navigateFile('prev'); // In Arabic, Right Arrow moves to a "previous" (higher index) file
        } else {
            navigateFile('next'); // In English, Right Arrow moves to the "next" file
        }
    } else if (e.key === 'ArrowLeft') {
        const lang = localStorage.getItem('language') || 'ar';
        if (lang === 'ar') {
            navigateFile('next'); // In Arabic, Left Arrow moves to "next" (lower index)
        } else {
            navigateFile('prev'); // In English, Left Arrow moves to "previous"
        }
    }
});

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

async function initFileScanner() {
    const savedFile = localStorage.getItem('lastViewedFile');
    if (savedFile) {
        loadFileContent(savedFile);
    }

    const maxAttempts = 10000;
    const chunkSize = 20; // Smaller chunk size to avoid server rate-limiting

    for (let i = 1; i <= maxAttempts; i += chunkSize) {
        const chunk = [];
        for (let j = i; j < i + chunkSize && j <= maxAttempts; j++) {
            chunk.push(j);
        }

        // Fetch a chunk of files in parallel
        const results = await Promise.all(chunk.map(async (num) => {
            const filename = `${num}.txt`;
            try {
                const response = await fetch(filename, { method: 'HEAD' });
                return response.ok ? { num, filename } : null;
            } catch (e) {
                return null;
            }
        }));

        // Process results in the correct order within the chunk
        results.forEach(res => {
            if (res) {
                availableFiles.push(res.filename);

                const li = document.createElement('li');
                li.className = 'file-item';
                li.setAttribute('data-filename', res.filename);
                li.textContent = `${res.num}`;
                li.onclick = () => loadFileContent(res.filename);

                if (res.filename === savedFile) {
                    li.classList.add('active');
                }

                li.style.setProperty('--i', availableFiles.length);
                fileList.appendChild(li);
            }
        });
    }

    clearInvalidCache(availableFiles);
    preFetchFiles(availableFiles);
}

initFileScanner();''',

        'style.css': ''':root {
    --sidebar-width: 280px;
    --primary-color: #00838f;
    --accent-color: #00bcd4;
    --bg-color: #f4f7f6;
    --text-color: #2c3e50;
    --panel-bg: #ffffff;
    --panel-bg-rgba: rgba(255, 255, 255, 0.8);
    --border-color: #006064;
    --shadow-color: rgba(0,0,0,0.1);
    --header-height: 60px;
    --viewer-font: 'Cairo', sans-serif;

    /* Design System Modernization */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --shadow-soft: 0 8px 24px var(--shadow-color);

    /* Motion System */
    --transition-speed-fast: 0.2s;
    --transition-speed-normal: 0.3s;
    --transition-speed-slow: 0.5s;
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
}

* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

[data-theme="dark"] {
    --bg-color: #121212;
    --text-color: #e0e0e0;
    --panel-bg: #1e1e1e;
    --panel-bg-rgba: rgba(30, 30, 30, 0.8);
    --primary-color: #006064;
    --accent-color: #00bcd4;
    --border-color: #00838f;
    --shadow-color: rgba(0,0,0,0.5);
}

@keyframes appEntry {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes bottomBarEntry {
    from { opacity: 0; transform: translateX(-50%) translateY(20px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes contentFadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

body {
    font-family: 'Cairo', sans-serif;
    margin: 0;
    display: flex;
    height: 100vh;
    background-color: var(--bg-color);
    color: var(--text-color);
    overflow: hidden;
    transition: background-color var(--transition-speed-normal) var(--ease-in-out), color var(--transition-speed-normal) var(--ease-in-out);
    animation: appEntry var(--transition-speed-slow) var(--ease-out-expo);
}

/* SIDEBAR - Desktop optimized */
#sidebar {
    width: var(--sidebar-width);
    background-color: var(--primary-color);
    color: white;
    height: 100%;
    transition: transform var(--transition-speed-normal) cubic-bezier(0.32, 0.72, 0, 1), width var(--transition-speed-normal) var(--ease-out-expo);
    overflow-y: auto;
    overflow-x: hidden;
    flex-shrink: 0;
    z-index: 100;
    box-shadow: 2px 0 10px var(--shadow-color);
}
#sidebar.hidden {
    width: 0 !important;
    opacity: 0;
    pointer-events: none;
    transform: translateX(100%); /* RTL slide out */
}

[dir="ltr"] #sidebar.hidden {
    transform: translateX(-100%); /* LTR slide out */
}
.sidebar-content {
    width: var(--sidebar-width);
}
#sidebar h2 {
    padding: 20px;
    font-size: 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
#file-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.file-item {
    padding: 14px 16px;
    cursor: pointer;
    margin: 4px 12px;
    border-radius: var(--radius-md);
    transition: all var(--transition-speed-fast) var(--ease-out-expo);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    justify-content: space-between;

    /* Staggered entry state */
    opacity: 0;
    transform: translateX(15px);
    transition:
        opacity var(--transition-speed-normal) var(--ease-out-expo),
        transform var(--transition-speed-normal) var(--ease-out-expo),
        all var(--transition-speed-slow) var(--ease-out-expo);
    transition-delay: calc(var(--i) * 0.03s);
}

#sidebar:not(.hidden) .file-item {
    opacity: 1;
    transform: translateX(0);
}
.file-item:hover, .file-item.active {
    background-color: var(--accent-color);
    color: white;
    padding-right: 30px;
}

.lang-transition {
    opacity: 0.6;
    transform: scale(0.98);
    transition: opacity 0.1s ease, transform 0.1s ease;
}

/* MAIN CONTENT */
#main-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}
#toolbar {
    height: 64px;
    padding: 0 20px;
    background: var(--panel-bg-rgba);
    box-shadow: 0 8px 30px var(--shadow-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all var(--transition-speed-normal) var(--ease-in-out);
    z-index: 50;
    border-bottom: 1px solid var(--border-color);
    backdrop-filter: blur(10px);
}
.toolbar-right, .toolbar-left, .toolbar-center {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
}
.toolbar-right {
    flex: 1;
    justify-content: flex-start;
}
.toolbar-left {
    flex: 1;
    justify-content: flex-end;
}
.toolbar-center {
    flex: 0 0 auto;
    justify-content: center;
    font-size: 1.1rem;
    padding: 10px;
}

button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 10px 18px;
    cursor: pointer;
    border-radius: var(--radius-md);
    font-weight: 600;
    transition: all var(--transition-speed-fast) var(--ease-out-back);
    font-family: 'Cairo', sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    min-height: 44px;
}
button:active {
    transform: scale(0.96);
}
button:hover {
    background: var(--accent-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-soft);
}

#current-filename {
    font-weight: 600;
    font-size: 0.95rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

#viewer {
    padding: 30px 30px 100px 30px;
    font-family: var(--viewer-font);
    font-size: 1.3rem;
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-y: auto;
    flex-grow: 1;
    width: 100%;
    scroll-behavior: smooth;
}

.viewer-animating {
    animation: contentFadeIn var(--transition-speed-normal) var(--ease-out-expo);
}

/* BOTTOM NAVIGATION BAR */
#bottom-bar {
    position: fixed;
    bottom: calc(25px + env(safe-area-inset-bottom));
    left: 50%;
    transform: translateX(-50%);
    background: var(--panel-bg-rgba);
    color: var(--text-color);
    padding: 12px 20px;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-soft);
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 1000;
    border: 1px solid var(--border-color);
    backdrop-filter: blur(16px);
    transition: background-color var(--transition-speed-normal) var(--ease-in-out), border-color var(--transition-speed-normal) var(--ease-in-out);
    animation: bottomBarEntry var(--transition-speed-slow) var(--ease-out-expo);
}
#font-size-display {
    font-weight: 800;
    min-width: 35px;
    text-align: center;
    font-size: 0.9rem;
}
.nav-btn {
    padding: 8px 20px;
    border-radius: 20px;
}
.font-btn {
    width: 35px;
    height: 35px;
    padding: 0;
    justify-content: center;
    border-radius: 50%;
}

.placeholder {
    color: #888;
    text-align: center;
    margin-top: 100px;
    font-size: 1.1rem;
}

/* RESPONSIVE DESIGN */

/* Tablet (up to 1024px) */
@media (max-width: 1024px) {
    :root {
        --sidebar-width: 240px;
    }
    #viewer {
        padding: 20px;
    }
}

/* Phone (up to 768px) */
@media (max-width: 768px) {
    body {
        flex-direction: column;
    }
    button {
        padding: 8px 12px;
        min-height: 40px;
        font-size: 0.85rem;
    }
    #sidebar {
        position: fixed;
        right: 0;
        top: 0;
        width: 280px !important; /* Fixed width instead of 100% */
        max-width: 80%;
        box-shadow: -2px 0 10px var(--shadow-color);
        transform: translateX(100%); /* Start hidden */
        z-index: 200;
        transition: transform 0.3s ease;
    }
    [dir="ltr"] #sidebar {
        right: auto;
        left: 0;
        box-shadow: 2px 0 10px var(--shadow-color);
        transform: translateX(-100%);
    }
    #sidebar.hidden {
        transform: translateX(100%);
        opacity: 1; /* Keep opacity 1 for smoother slide */
        width: 280px !important;
    }
    [dir="ltr"] #sidebar.hidden {
        transform: translateX(-100%);
    }
    #sidebar:not(.hidden) {
        transform: translateX(0);
        opacity: 1;
    }
    #sidebar-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 150;
        display: none;
        backdrop-filter: blur(2px);
    }
    #sidebar-overlay.active {
        display: block;
    }
    .sidebar-content {
        width: 280px;
        padding-bottom: 100px;
    }
    #toolbar {
        padding: 10px 10px;
    }
    #current-filename {
        font-size: 0.9rem;
        max-width: 30%;
    }
    #viewer {
        padding: 20px 15px 120px 15px;
        font-size: 1.2rem;
    }
    #bottom-bar {
        width: 90%;
        justify-content: space-between;
        padding: 5px 10px;
    }
    .nav-btn {
        padding: 6px 10px;
        font-size: 0.8rem;
    }
    #toggle-btn {
        padding: 5px 10px;
        font-size: 0.8rem;
    }
    /* Hide text labels on phones to make buttons smaller/icon-only */
    #toggle-btn {
        font-size: 0;
    }
    #toggle-btn::before {
        content: '☰';
        font-size: 1.2rem;
    }
    #theme-btn {
        font-size: 0;
    }
    #theme-btn::before {
        content: '🌙';
        font-size: 1.2rem;
    }
    /* Special handling for theme button text updates via JS */
    [data-theme="dark"] #theme-btn::before {
        content: '☀️';
    }

    #clear-data-btn {
        font-size: 0;
    }
    #clear-data-btn::before {
        content: '🗑️';
        font-size: 1.2rem;
    }

    .toolbar-left button {
        padding: 8px;
    }
}

/* Tiny Phone (up to 480px) */
@media (max-width: 480px) {
    #toolbar .toolbar-center {
        display: none;
    }
    #toolbar .toolbar-right {
        flex-grow: 1;
    }
    #toolbar .toolbar-right button {
        width: auto;
        min-width: 40px;
        justify-content: center;
    }
    #bottom-bar {
        gap: 5px;
    }
    .nav-btn {
        flex: 1;
        text-align: center;
        padding: 8px 5px;
        font-size: 0.75rem;
    }
}

.toast {
    position: fixed;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    z-index: 3000;
    opacity: 0;
    transition: opacity 0.3s ease, transform 0.3s ease;
    pointer-events: none;
    white-space: nowrap;
    backdrop-filter: blur(5px);
}

.toast.show {
    opacity: 1;
    transform: translateX(-50%) translateY(-10px);
}'''
    }

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create each file
    for filename, content in files.items():
        filepath = os.path.join(current_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✅ Created: {filename}')
        except Exception as e:
            print(f'❌ Error creating {filename}: {e}')

    print(f'\\n📁 All files created in: {current_dir}')
    print('📄 Files created: index.html, script.js, style.css')
    print('💡 Open index.html in your browser to view the app.')

if __name__ == '__main__':
    create_files()

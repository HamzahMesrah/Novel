const sidebar = document.getElementById('sidebar');
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
        viewer_placeholder: 'الرجاء اختيار ملف نصي من القائمة الجانبية لعرض محتواه.<br>(استخدم الأسهم ← → للتنقل بين المل[...]',
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
    if (confirm('هل أنت متأكد من أنك تريد مسح جميع البيانات والإعدادات؟\nAre you sure you want to clear all data and settings?')) {
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

const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
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

        viewer.textContent = text + '\n\n\n\n\n';
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

initFileScanner();

const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggle-btn');
const themeBtn = document.getElementById('theme-btn');
const fontUpBtn = document.getElementById('font-up-btn');
const fontDownBtn = document.getElementById('font-down-btn');
const fontSizeDisplay = document.getElementById('font-size-display');
const fileList = document.getElementById('file-list');
const viewer = document.getElementById('viewer');
const currentFilename = document.getElementById('current-filename');

// Array to keep track of all discovered files for navigation
let availableFiles = [];

// إدارة الثيم
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeButtonText(currentTheme);

// إدارة حجم الخط
let currentFontSize = parseFloat(localStorage.getItem('fontSize')) || 1.3;
function updateFontSize() {
    viewer.style.fontSize = `${currentFontSize}rem`;
    localStorage.setItem('fontSize', currentFontSize);
    fontSizeDisplay.textContent = currentFontSize.toFixed(1);
}
updateFontSize();

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

themeBtn.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    let newTheme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButtonText(newTheme);
});

function updateThemeButtonText(theme) {
    themeBtn.textContent = theme === 'dark' ? '☀️ الوضع الفاتح' : '🌙 الوضع الداكن';
}

toggleBtn.addEventListener('click', () => {
    toggleSidebar();
});

function toggleSidebar() {
    sidebar.classList.toggle('hidden');
    localStorage.setItem('sidebarHidden', sidebar.classList.contains('hidden'));
}

// Initialize sidebar state
if (localStorage.getItem('sidebarHidden') === 'true') {
    sidebar.classList.add('hidden');
}

const prevBtn = document.getElementById('next-btn');
const nextBtn = document.getElementById('prev-btn');
prevBtn.addEventListener('click', () => navigateFile('prev'));
nextBtn.addEventListener('click', () => navigateFile('next'));

async function loadFileContent(filename) {
    if (!filename) return;
    try {
        const response = await fetch(filename);
        if (!response.ok) throw new Error('الملف غير موجود');
        const text = await response.text();
        viewer.textContent = text;
        viewer.scrollTop = 0;
        currentFilename.textContent = filename.replace('.txt', '');

        localStorage.setItem('lastViewedFile', filename);

        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-filename') === filename);
        });
    } catch (err) {
        viewer.innerHTML = `<span style="color:red">خطأ في تحميل الملف: ${err.message}</span>`;
    }
}

// Navigation Logic
function navigateFile(direction) {
    const currentFile = localStorage.getItem('lastViewedFile');
    const currentIndex = availableFiles.indexOf(currentFile);

    if (currentIndex === -1) return; // No file currently selected

    if (direction === 'prev' && currentIndex < availableFiles.length - 1) {
        loadFileContent(availableFiles[currentIndex + 1]);
    } else if (direction === 'next' && currentIndex > 0) {
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
        // Since it's RTL, Right Arrow usually means "Next" or "Forward"
        navigateFile('next');
    } else if (e.key === 'ArrowLeft') {
        navigateFile('prev');
    }
});

async function initFileScanner() {
    let i = 1;
    const maxAttempts = 10000;
    const savedFile = localStorage.getItem('lastViewedFile');

    while (i <= maxAttempts) {
        const filename = `${i}.txt`;
        try {
            const response = await fetch(filename, { method: 'HEAD' });
            if (response.ok) {
                availableFiles.push(filename); // Add to our tracking array

                const li = document.createElement('li');
                li.className = 'file-item';
                li.setAttribute('data-filename', filename);
                li.textContent = `${i}`;
                li.onclick = () => loadFileContent(filename);
                fileList.appendChild(li);
            } else {
                break;
            }
        } catch (e) {
            // console.log(`Error scanning ${filename}`);
        }
        i++;
    }

    if (savedFile && availableFiles.includes(savedFile)) {
        loadFileContent(savedFile);
    }
}

initFileScanner();
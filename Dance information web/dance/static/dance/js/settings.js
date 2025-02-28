// 选项卡切换功能
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const saveButton = document.getElementById('saveSettings');
    const saveNotification = document.getElementById('saveNotification');
    let settings = {};

    // 加载保存的设置
    loadSettings();

    // 选项卡切换
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // 添加新的活动状态
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // 监听所有输入变化
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', () => {
            if (input.type === 'checkbox') {
                settings[input.name] = input.checked;
            } else {
                settings[input.name] = input.value;
            }
        });
    });

    // 保存设置
    saveButton.addEventListener('click', () => {
        // 保存设置到localStorage
        localStorage.setItem('danceGroupSettings', JSON.stringify(settings));

        // 显示保存提示
        saveNotification.style.display = 'block';
        setTimeout(() => {
            saveNotification.style.display = 'none';
        }, 3000);
    });

    // 加载设置
    function loadSettings() {
        const savedSettings = localStorage.getItem('danceGroupSettings');
        if (savedSettings) {
            settings = JSON.parse(savedSettings);
            // 应用保存的设置
            Object.entries(settings).forEach(([key, value]) => {
                const input = document.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value;
                    } else {
                        input.value = value;
                    }
                }
            });
        }
    }
});

// 深色模式切换逻辑
const themeToggle = document.getElementById('themeToggle');

// 从 localStorage 中获取保存的主题
const savedTheme = localStorage.getItem('theme');

themeToggle.checked = document.documentElement.getAttribute('data-theme') === 'dark';
// 监听切换按钮的变化
themeToggle.addEventListener('change', (e) => {
    const newTheme = e.target.checked ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// 如果有保存的主题，应用它
if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.checked = savedTheme === 'dark';
}

// 监听切换按钮的变化
themeToggle.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        console.log("1");
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        console.log("2");
    }
});

// 检测系统主题偏好
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

// 如果没有保存的主题，使用系统偏好
if (!savedTheme) {
    if (prefersDark.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeToggle.checked = true;
    }
}
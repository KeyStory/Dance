// 填充年份选项
const yearSelect = document.getElementById('year');
const currentYear = new Date().getFullYear();
const minAge = 7;  // 最小年龄
const maxAge = 70; // 最大年龄

// 计算最小和最大出生年份
const minBirthYear = currentYear - maxAge;  // 70岁对应的出生年
const maxBirthYear = currentYear - minAge;  // 7岁对应的出生年

for (let year = maxBirthYear; year >= minBirthYear; year--) {
    const option = document.createElement('option');
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
}

// 填充月份选项
const monthSelect = document.getElementById('month');
for (let month = 1; month <= 12; month++) {
    const option = document.createElement('option');
    option.value = month;
    option.textContent = month;
    monthSelect.appendChild(option);
}

// 更新日期选项
function updateDays() {
    const daySelect = document.getElementById('day');
    const year = yearSelect.value;
    const month = monthSelect.value;
    
    daySelect.innerHTML = '<option value="">Day</option>';
    
    if (year && month) {
        const daysInMonth = new Date(year, month, 0).getDate();
        for (let day = 1; day <= daysInMonth; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day;
            daySelect.appendChild(option);
        }
    }
}

yearSelect.addEventListener('change', updateDays);
monthSelect.addEventListener('change', updateDays);

// 添加 reCAPTCHA 相关函数
let recaptchaCompleted = false;

function onRecaptchaSuccess(token) {
    recaptchaCompleted = true;
    document.getElementById('recaptcha-error').textContent = '';
}

function onRecaptchaExpired() {
    recaptchaCompleted = false;
    grecaptcha.reset();
}

// 获取用户名输入框
const usernameInput = document.getElementById('username');

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// 检查用户名函数
async function checkUsername() {
    const username = usernameInput.value.trim();
    const errorElement = document.getElementById('username-error');
    const formGroup = usernameInput.closest('.form-group');
    
    // 如果用户名为空，不进行检查
    if (!username) {
        formGroup.classList.add('error');
        errorElement.textContent = 'Username is required';
        errorElement.style.display = 'block';
        return;
    }

    try {
        // 发送请求到后端检查用户名
        const response = await fetch(`/check-username/?username=${encodeURIComponent(username)}`);
        const data = await response.json();

        if (data.exists) {
            // 用户名已存在
            formGroup.classList.add('error');
            errorElement.textContent = 'Username already exists';
            errorElement.style.display = 'block';
        } else {
            // 用户名可用
            formGroup.classList.remove('error');
            errorElement.style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking username:', error);
        errorElement.textContent = 'Error checking username availability';
        errorElement.style.display = 'block';
    }
}

// 添加输入事件监听器（使用防抖）
usernameInput.addEventListener('input', debounce(checkUsername, 500));

// 表单提交验证
document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // 验证用户名
    const username = usernameInput.value.trim();
    if (!username) {
        const errorElement = document.getElementById('username-error');
        const formGroup = usernameInput.closest('.form-group');
        formGroup.classList.add('error');
        errorElement.textContent = 'Username is required';
        errorElement.style.display = 'block';
        return;
    }
});

// 验证函数
const validators = {
    username: (value) => {
        if (!value.trim()) return 'Username is required';
        return '';
    },
    password: (value) => {
        if (!value) return 'Password is required';
        if (value.length < 8) return 'Password must be at least 8 characters';
        return '';
    },
    'confirm-password': (value) => {
        const password = document.getElementById('password').value;
        if (!value) return 'Please confirm your password';
        if (value !== password) return 'Passwords do not match';
        return '';
    },
    email: (value) => {
        if (!value.trim()) return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
        return '';
    }
};

// 添加实时验证
Object.keys(validators).forEach(fieldName => {
    const field = document.getElementById(fieldName);
    
    // 输入时验证（用于确认密码）
    field.addEventListener('input', () => {
        if (fieldName === 'password') {
            // 当密码改变时，如果确认密码已有输入，则重新验证确认密码
            const confirmPassword = document.getElementById('confirm-password');
            if (confirmPassword.value) {
                validateField('confirm-password');
            }
        }
    });

    // 失去焦点时验证
    field.addEventListener('blur', () => {
        validateField(fieldName);
    });
});

// 验证单个字段
function validateField(fieldName) {
    const field = document.getElementById(fieldName);
    const errorMessage = validators[fieldName](field.value);
    const formGroup = field.closest('.form-group');
    const errorElement = formGroup.querySelector('.error-message');

    if (errorMessage) {
        formGroup.classList.add('error');
        errorElement.textContent = errorMessage;
        return false;
    } else {
        formGroup.classList.remove('error');
        errorElement.textContent = '';
        return true;
    }
}

// 表单提交验证
document.getElementById('signupForm').addEventListener('submit', function(e) {
    e.preventDefault();
    let isValid = true;

    // 验证所有必填字段
    Object.keys(validators).forEach(fieldName => {
        if (!validateField(fieldName)) {
            isValid = false;
        }
    });

    if (isValid) {
        console.log('Form submitted successfully');
        // 这里添加表单提交逻辑
    }
});

document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // 验证 reCAPTCHA
    if (!recaptchaCompleted) {
        document.getElementById('recaptcha-error').textContent = 'Please complete the reCAPTCHA';
        return;
    }

    // 获取 reCAPTCHA token
    const recaptchaToken = grecaptcha.getResponse();
    
    // 获取表单数据
    const formData = {
        username: document.getElementById('username').value.trim(),
        password: document.getElementById('password').value,
        email: document.getElementById('email').value.trim(),
        job: document.getElementById('job').value,
        birth_year: document.getElementById('year').value,
        birth_month: document.getElementById('month').value,
        birth_day: document.getElementById('day').value,
        'g-recaptcha-response': recaptchaToken
    };
    
    // 验证表单
    if (!formData.username || !formData.password || !formData.email) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        // 发送注册请求
        const response = await fetch('/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Registration successful!');
            // 注册成功后的操作，比如跳转到登录页
            window.location.href = '/app_users_login/';
        } else {
            alert('Registration failed: ' + data.message);
            grecaptcha.reset();
            recaptchaCompleted = false;
        }
    } catch (error) {
        console.error('Error during registration:', error);
        alert('An error occurred during registration');
        grecaptcha.reset();
        recaptchaCompleted = false;
    }
});

// 获取CSRF令牌的函数
function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue;
}
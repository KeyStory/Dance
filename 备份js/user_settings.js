document.addEventListener('DOMContentLoaded', function() {
    // 密码修改相关
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const cancelPasswordBtn = document.getElementById('cancelPasswordBtn');
    const passwordForm = document.getElementById('passwordForm');

    changePasswordBtn.addEventListener('click', function() {
        passwordForm.classList.remove('hidden');
        changePasswordBtn.classList.add('hidden');
    });

    cancelPasswordBtn.addEventListener('click', function() {
        passwordForm.classList.add('hidden');
        changePasswordBtn.classList.remove('hidden');
    });

    passwordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const currentPassword = passwordForm.querySelector('input[placeholder="Please enter your current password"]').value;
        const newPassword = passwordForm.querySelector('input[placeholder="Please enter new password"]').value;
        const confirmPassword = passwordForm.querySelector('input[placeholder="Please enter your new password again"]').value;

        // 验证新密码
        if (newPassword !== confirmPassword) {
            alert('New passwords do not match');
            return;
        }

        if (newPassword.length < 6) {
            alert('New password must be at least 6 characters long');
            return;
        }

        try {
            const response = await fetch('/change_password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                alert('Password updated successfully');
                passwordForm.classList.add('hidden');
                changePasswordBtn.classList.remove('hidden');
                passwordForm.reset();
            } else {
                alert(data.message || 'Failed to update password');
            }
        } catch (error) {
            alert('An error occurred while updating password');
            console.error('Error:', error);
        }
    });

    // 获取CSRF Token的辅助函数
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 头像上传
    const avatarInput = document.getElementById('avatarInput');
    const userAvatar = document.getElementById('userAvatar');

    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 验证文件类型
            if (!file.type.match('image/jpeg') && !file.type.match('image/png')) {
                alert('请上传 JPG 或 PNG 格式的图片');
                return;
            }
            // 验证文件大小（2MB = 2 * 1024 * 1024 bytes）
            if (file.size > 2 * 1024 * 1024) {
                alert('图片大小不能超过 2MB');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                userAvatar.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // 个人简介字数统计
    const bioTextarea = document.getElementById('bio');
    const bioCount = document.getElementById('bioCount');

    bioTextarea.addEventListener('input', function() {
        const count = this.value.length;
        bioCount.textContent = count;
        
        // 字数超限提示
        if (count > 190) {
            bioCount.style.color = '#e53e3e';
        } else {
            bioCount.style.color = 'inherit';
        }
    });

    // 省市联动
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');

    // 省份数据
    const provinces = [
        { id: 'beijing', name: '北京市' },
        { id: 'shanghai', name: '上海市' },
        { id: 'guangdong', name: '广东省' },
        { id: 'jiangsu', name: '江苏省' },
        { id: 'zhejiang', name: '浙江省' },
        { id: 'sichuan', name: '四川省' }
    ];

    // 城市数据
    const cities = {
        beijing: [
            { id: 'haidian', name: '海淀区' },
            { id: 'chaoyang', name: '朝阳区' },
            { id: 'dongcheng', name: '东城区' },
            { id: 'xicheng', name: '西城区' }
        ],
        shanghai: [
            { id: 'pudong', name: '浦东新区' },
            { id: 'huangpu', name: '黄浦区' },
            { id: 'xuhui', name: '徐汇区' },
            { id: 'putuo', name: '普陀区' }
        ],
        guangdong: [
            { id: 'guangzhou', name: '广州市' },
            { id: 'shenzhen', name: '深圳市' },
            { id: 'dongguan', name: '东莞市' },
            { id: 'foshan', name: '佛山市' }
        ],
        jiangsu: [
            { id: 'nanjing', name: '南京市' },
            { id: 'suzhou', name: '苏州市' },
            { id: 'wuxi', name: '无锡市' },
            { id: 'changzhou', name: '常州市' }
        ],
        zhejiang: [
            { id: 'hangzhou', name: '杭州市' },
            { id: 'ningbo', name: '宁波市' },
            { id: 'wenzhou', name: '温州市' },
            { id: 'shaoxing', name: '绍兴市' }
        ],
        sichuan: [
            { id: 'chengdu', name: '成都市' },
            { id: 'mianyang', name: '绵阳市' },
            { id: 'deyang', name: '德阳市' },
            { id: 'leshan', name: '乐山市' }
        ]
    };

    // 初始化省份下拉框
    provinces.forEach(province => {
        const option = document.createElement('option');
        option.value = province.id;
        option.textContent = province.name;
        provinceSelect.appendChild(option);
    });

    // 省份变化时更新城市
    provinceSelect.addEventListener('change', function() {
        citySelect.innerHTML = '<option value="">请选择城市</option>';
        
        const selectedProvince = this.value;
        if (selectedProvince && cities[selectedProvince]) {
            cities[selectedProvince].forEach(city => {
                const option = document.createElement('option');
                option.value = city.id;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });
            citySelect.disabled = false;
        } else {
            citySelect.disabled = true;
        }
    });

    // 邮箱验证按钮点击事件
    const verifyEmailBtn = document.querySelector('.input-group .btn-secondary');
    verifyEmailBtn.addEventListener('click', function() {
        const emailInput = this.parentElement.querySelector('input[type="email"]');
        const email = emailInput.value;
        
        // 简单的邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('请输入有效的邮箱地址');
            return;
        }

        // TODO: 发送邮箱验证请求到服务器
        alert('验证邮件已发送，请查收！');
    });

    // 手机验证按钮点击事件
    const verifyPhoneBtn = document.querySelector('.input-group:last-of-type .btn-secondary');
    verifyPhoneBtn.addEventListener('click', function() {
        const phoneInput = this.parentElement.querySelector('input[type="tel"]');
        const phone = phoneInput.value;
        
        // 简单的手机号格式验证（中国大陆手机号）
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(phone)) {
            alert('请输入有效的手机号码');
            return;
        }

        // TODO: 发送手机验证码请求到服务器
        alert('验证码已发送，请注意查收！');
    });

    // 保存设置
    const saveButton = document.querySelector('.button-container .btn-primary');
    saveButton.addEventListener('click', function() {
        // 收集表单数据
        const formData = {
            username: document.querySelector('input[type="text"]').value,
            email: document.querySelector('input[type="email"]').value,
            phone: document.querySelector('input[type="tel"]').value,
            province: provinceSelect.value,
            city: citySelect.value,
            bio: bioTextarea.value
        };

        // 验证必填字段
        if (!formData.username) {
            alert('请输入用户名');
            return;
        }

        // TODO: 发送数据到服务器
        console.log('保存的数据：', formData);
        alert('设置保存成功！');
    });

    // 初始化禁用城市选择
    citySelect.disabled = true;
});
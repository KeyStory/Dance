// 显示提示消息
function showMessage(message, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert ${isError ? 'alert-danger' : 'alert-success'}`;
    messageDiv.textContent = message;
    document.querySelector('.container').insertBefore(messageDiv, document.querySelector('.card'));
    
    // 3秒后自动消失
    setTimeout(() => messageDiv.remove(), 3000);
}

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
        
        const currentPassword = passwordForm.querySelector('#current-password').value;
        const newPassword = passwordForm.querySelector('#new-password').value;
        const confirmPassword = passwordForm.querySelector('#confirm-password').value;

        // 验证新密码
        if (newPassword !== confirmPassword) {
            alert('New passwords do not match');
            return;
        }

        if (newPassword.length < 8) {
            alert('New password must be at least 8 characters long');
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
                alert('Please upload images in JPG or PNG format');
                return;
            }
            // 验证文件大小（2MB = 2 * 1024 * 1024 bytes）
            if (file.size > 2 * 1024 * 1024) {
                alert('Image size cannot exceed 2MB');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                userAvatar.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // 保存设置
    const saveButton = document.getElementById('save_button');
    saveButton.addEventListener('click', async function() {
        const email = document.getElementById('email_input').value.trim();
        const username = document.getElementById('username_input').value.trim();

        try {
            const updateResponse = await fetch('/api/update_personal_info/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    username: username,
                    email: email
                })
            });
            
            // TODO: 处理用户名更新和头像上传
            showMessage('Settings saved successfully');
            
        } catch (error) {
            showMessage('Failed to save settings, please try again later', true);
        }
    });
});
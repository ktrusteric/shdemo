// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否已登录
    if (utils.isLoggedIn()) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    // 绑定表单提交事件
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', handleLogin);
});

// 处理登录
async function handleLogin(event) {
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    try {
        // 禁用提交按钮
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>登录中...';
        
        // 发送登录请求
        const response = await utils.apiRequest(API_ENDPOINTS.login, {
            method: 'POST',
            body: JSON.stringify(loginData)
        });
        
        // 登录成功
        if (response.success) {
            // 保存令牌和用户信息
            utils.setToken(response.token);
            utils.setUserInfo(response.user);
            
            // 显示成功消息
            utils.showAlert('登录成功！即将跳转到控制台...', 'success');
            
            // 跳转到控制台
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            throw new Error(response.message || '登录失败');
        }
        
    } catch (error) {
        // 登录失败
        utils.showAlert(error.message || '登录失败，请检查用户名和密码', 'danger');
        
        // 恢复提交按钮
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '登录';
    }
} 
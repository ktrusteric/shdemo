// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', async () => {
    // 加载地区列表
    await loadRegions();
    
    // 加载交易品种
    await loadTradingProducts();
    
    // 绑定表单提交事件
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', handleRegister);
});

// 加载地区列表
async function loadRegions() {
    try {
        const data = await utils.apiRequest(API_ENDPOINTS.regions);
        const regionSelect = document.getElementById('region');
        
        data.regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            regionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('加载地区列表失败:', error);
        utils.showAlert('加载地区列表失败', 'danger');
    }
}

// 加载交易品种
async function loadTradingProducts() {
    try {
        const data = await utils.apiRequest(API_ENDPOINTS.tradingProducts);
        const productsContainer = document.getElementById('tradingProducts');
        
        data.products.forEach((product, index) => {
            const checkDiv = document.createElement('div');
            checkDiv.className = 'form-check';
            checkDiv.innerHTML = `
                <input class="form-check-input" type="checkbox" 
                       name="trading_products" value="${product}" 
                       id="product${index}">
                <label class="form-check-label" for="product${index}">
                    ${product}
                </label>
            `;
            productsContainer.appendChild(checkDiv);
        });
    } catch (error) {
        console.error('加载交易品种失败:', error);
        utils.showAlert('加载交易品种失败', 'danger');
    }
}

// 处理注册
async function handleRegister(event) {
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    
    // 验证密码
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    
    if (password !== confirmPassword) {
        utils.showAlert('两次输入的密码不一致', 'danger');
        return;
    }
    
    // 获取选中的交易品种
    const tradingProducts = [];
    const checkboxes = document.querySelectorAll('input[name="trading_products"]:checked');
    checkboxes.forEach(checkbox => {
        tradingProducts.push(checkbox.value);
    });
    
    if (tradingProducts.length === 0) {
        utils.showAlert('请至少选择一个交易品种', 'danger');
        return;
    }
    
    // 构建注册数据
    const registerData = {
        username: formData.get('username'),
        password: formData.get('password'),
        email: formData.get('email'),
        region: formData.get('region'),
        trading_products: tradingProducts,
        company_name: formData.get('company_name') || null
    };
    
    try {
        // 禁用提交按钮
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>注册中...';
        
        // 发送注册请求
        const response = await utils.apiRequest(API_ENDPOINTS.register, {
            method: 'POST',
            body: JSON.stringify(registerData)
        });
        
        // 注册成功
        utils.showAlert('注册成功！即将跳转到登录页面...', 'success');
        
        // 3秒后跳转到登录页面
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 3000);
        
    } catch (error) {
        // 注册失败
        utils.showAlert(error.message || '注册失败，请重试', 'danger');
        
        // 恢复提交按钮
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '注册';
    }
} 
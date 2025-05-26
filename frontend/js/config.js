// API配置
const API_BASE_URL = window.location.origin + '/api';

// API端点
const API_ENDPOINTS = {
    // 认证相关
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
    regions: `${API_BASE_URL}/auth/regions`,
    tradingProducts: `${API_BASE_URL}/auth/trading-products`,
    systemUsers: `${API_BASE_URL}/auth/system-users`,
    
    // 用户相关
    profile: `${API_BASE_URL}/user/profile`,
    upgrade: `${API_BASE_URL}/user/upgrade`,
    behavior: `${API_BASE_URL}/user/behavior`,
    userTags: `${API_BASE_URL}/user/tags`,
    
    // 能源数据相关
    news: `${API_BASE_URL}/energy/news`,
    prices: `${API_BASE_URL}/energy/prices`,
    latestPrices: `${API_BASE_URL}/energy/prices/latest`,
    deals: `${API_BASE_URL}/energy/deals`,
    reports: `${API_BASE_URL}/energy/reports`,
    indexes: `${API_BASE_URL}/energy/indexes`,
    
    // 推荐相关
    personalized: `${API_BASE_URL}/recommendation/personalized`,
    guessYouLike: `${API_BASE_URL}/recommendation/guess-you-like`,
    hotTopics: `${API_BASE_URL}/recommendation/hot-topics`
};

// 本地存储键名
const STORAGE_KEYS = {
    token: 'energy_trading_token',
    userInfo: 'energy_trading_user'
};

// 工具函数
const utils = {
    // 获取存储的令牌
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.token);
    },
    
    // 设置令牌
    setToken(token) {
        localStorage.setItem(STORAGE_KEYS.token, token);
    },
    
    // 清除令牌
    clearToken() {
        localStorage.removeItem(STORAGE_KEYS.token);
    },
    
    // 获取用户信息
    getUserInfo() {
        const userStr = localStorage.getItem(STORAGE_KEYS.userInfo);
        return userStr ? JSON.parse(userStr) : null;
    },
    
    // 设置用户信息
    setUserInfo(userInfo) {
        localStorage.setItem(STORAGE_KEYS.userInfo, JSON.stringify(userInfo));
    },
    
    // 清除用户信息
    clearUserInfo() {
        localStorage.removeItem(STORAGE_KEYS.userInfo);
    },
    
    // 清除所有存储
    clearAll() {
        utils.clearToken();
        utils.clearUserInfo();
    },
    
    // 检查是否已登录
    isLoggedIn() {
        return !!utils.getToken();
    },
    
    // 发送API请求
    async apiRequest(url, options = {}) {
        const token = utils.getToken();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || '请求失败');
            }
            
            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    },
    
    // 显示提示消息
    showAlert(message, type = 'info', elementId = 'alertMessage') {
        const alertElement = document.getElementById(elementId);
        if (alertElement) {
            alertElement.className = `alert alert-${type}`;
            alertElement.textContent = message;
            alertElement.classList.remove('d-none');
            
            // 3秒后自动隐藏
            setTimeout(() => {
                alertElement.classList.add('d-none');
            }, 3000);
        }
    },
    
    // 记录用户行为
    async recordBehavior(behaviorType, details) {
        if (!utils.isLoggedIn()) return;
        
        try {
            await utils.apiRequest(API_ENDPOINTS.behavior, {
                method: 'POST',
                body: JSON.stringify({
                    behavior_type: behaviorType,
                    details: details
                })
            });
        } catch (error) {
            console.error('记录行为失败:', error);
        }
    }
}; 
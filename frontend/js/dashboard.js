// 仪表盘JavaScript

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 检查登录状态
    if (!utils.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    
    // 初始化页面
    initDashboard();
    
    // 绑定事件
    bindEvents();
    
    // 加载初始数据
    loadOverviewData();
    loadPersonalizedRecommendations();
});

// 初始化仪表盘
function initDashboard() {
    // 显示用户信息
    const userInfo = utils.getUserInfo();
    if (userInfo) {
        document.getElementById('userName').textContent = userInfo.username;
        document.getElementById('userType').textContent = userInfo.user_type === 'paid' ? '付费用户' : '免费用户';
        
        // 如果是付费用户，隐藏升级按钮
        if (userInfo.user_type === 'paid') {
            document.getElementById('upgradeBtn').style.display = 'none';
        }
    }
}

// 绑定事件
function bindEvents() {
    // 侧边栏导航
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');
            
            // 处理退出登录
            if (link.id === 'logoutBtn') {
                handleLogout();
                return;
            }
            
            // 切换活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // 显示对应内容
            showSection(target.substring(1));
        });
    });
    
    // 升级会员按钮
    document.getElementById('upgradeBtn').addEventListener('click', handleUpgrade);
}

// 显示指定部分
function showSection(sectionId) {
    // 隐藏所有部分
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // 显示指定部分
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.remove('d-none');
        
        // 根据部分加载数据
        switch(sectionId) {
            case 'overview':
                loadOverviewData();
                break;
            case 'news':
                loadNewsData();
                break;
            case 'prices':
                loadPriceData();
                break;
            case 'deals':
                loadDealsData();
                break;
            case 'reports':
                loadReportsData();
                break;
            case 'recommend':
                loadRecommendations();
                break;
            case 'profile':
                loadProfile();
                break;
        }
    }
}

// 加载概览数据
async function loadOverviewData() {
    try {
        // 获取今日资讯数量
        const newsResponse = await utils.apiRequest(`${API_ENDPOINTS.news}?limit=1`);
        document.getElementById('todayNewsCount').textContent = newsResponse.total || 0;
        
        // 获取最新价格
        const priceResponse = await utils.apiRequest(API_ENDPOINTS.latestPrices);
        if (priceResponse.data && priceResponse.data.length > 0) {
            const latestPrice = priceResponse.data[0];
            document.getElementById('latestPrice').textContent = `¥${latestPrice.price}`;
        }
        
        // 获取研报数量
        const reportResponse = await utils.apiRequest(`${API_ENDPOINTS.reports}?limit=1`);
        document.getElementById('reportCount').textContent = reportResponse.total || 0;
        
        // 记录用户行为
        utils.recordBehavior('view', { content_type: 'dashboard', duration: 0 });
        
    } catch (error) {
        console.error('加载概览数据失败:', error);
    }
}

// 加载个性化推荐
async function loadPersonalizedRecommendations() {
    try {
        const response = await utils.apiRequest(API_ENDPOINTS.personalized);
        const container = document.getElementById('personalizedContent');
        container.innerHTML = '';
        
        // 显示推荐的资讯
        if (response.news && response.news.length > 0) {
            response.news.slice(0, 3).forEach(news => {
                const card = createRecommendationCard('news', news);
                container.appendChild(card);
            });
        }
        
        // 显示推荐的研报
        if (response.reports && response.reports.length > 0) {
            response.reports.slice(0, 3).forEach(report => {
                const card = createRecommendationCard('report', report);
                container.appendChild(card);
            });
        }
        
    } catch (error) {
        console.error('加载个性化推荐失败:', error);
    }
}

// 创建推荐卡片
function createRecommendationCard(type, data) {
    const col = document.createElement('div');
    col.className = 'col-md-4';
    
    let icon, badge, title, content;
    
    if (type === 'news') {
        icon = 'fa-newspaper-o';
        badge = data.category;
        title = data.title;
        content = data.content.substring(0, 100) + '...';
    } else if (type === 'report') {
        icon = 'fa-file-text-o';
        badge = data.report_type;
        title = data.title;
        content = data.summary;
    }
    
    col.innerHTML = `
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <i class="fa ${icon} text-primary"></i>
                    <span class="badge bg-secondary">${badge}</span>
                </div>
                <h6 class="card-title">${title}</h6>
                <p class="card-text">${content}</p>
                <small class="text-muted">${data.recommendation_reason || ''}</small>
            </div>
        </div>
    `;
    
    return col;
}

// 加载资讯数据
async function loadNewsData() {
    try {
        const response = await utils.apiRequest(`${API_ENDPOINTS.news}?limit=20`);
        const tbody = document.getElementById('newsTableBody');
        tbody.innerHTML = '';
        
        if (response.data && response.data.length > 0) {
            response.data.forEach(news => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${news.title}</td>
                    <td><span class="badge bg-info">${news.category}</span></td>
                    <td>${news.source}</td>
                    <td>${new Date(news.publish_time).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-primary btn-action" onclick="viewNewsDetail('${news._id}')">
                            查看
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">暂无资讯数据</td></tr>';
        }
        
        // 记录行为
        utils.recordBehavior('view', { content_type: 'news', duration: 0 });
        
    } catch (error) {
        console.error('加载资讯数据失败:', error);
    }
}

// 加载价格数据
async function loadPriceData() {
    try {
        // 加载筛选选项
        await loadPriceFilters();
        
        // 加载价格数据
        const response = await utils.apiRequest(`${API_ENDPOINTS.prices}?days=7`);
        const tbody = document.getElementById('priceTableBody');
        tbody.innerHTML = '';
        
        if (response.data && response.data.length > 0) {
            response.data.forEach(price => {
                const row = document.createElement('tr');
                const changeClass = price.change_value > 0 ? 'up' : 'down';
                
                row.innerHTML = `
                    <td>${price.product_type}</td>
                    <td>${price.region}</td>
                    <td class="price-change ${changeClass}">${price.price}</td>
                    <td>${price.unit}</td>
                    <td>${new Date(price.price_date).toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">暂无价格数据</td></tr>';
        }
        
        // 记录行为
        utils.recordBehavior('view', { content_type: 'price', duration: 0 });
        
    } catch (error) {
        console.error('加载价格数据失败:', error);
    }
}

// 加载价格筛选器
async function loadPriceFilters() {
    try {
        // 加载产品类型
        const productsResponse = await utils.apiRequest(API_ENDPOINTS.tradingProducts);
        const productSelect = document.getElementById('priceProductFilter');
        productsResponse.products.forEach(product => {
            const option = document.createElement('option');
            option.value = product;
            option.textContent = product;
            productSelect.appendChild(option);
        });
        
        // 加载地区
        const regionsResponse = await utils.apiRequest(API_ENDPOINTS.regions);
        const regionSelect = document.getElementById('priceRegionFilter');
        regionsResponse.regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            regionSelect.appendChild(option);
        });
        
        // 绑定筛选事件
        productSelect.addEventListener('change', filterPrices);
        regionSelect.addEventListener('change', filterPrices);
        
    } catch (error) {
        console.error('加载筛选器失败:', error);
    }
}

// 筛选价格数据
async function filterPrices() {
    const product = document.getElementById('priceProductFilter').value;
    const region = document.getElementById('priceRegionFilter').value;
    
    let url = `${API_ENDPOINTS.prices}?days=7`;
    if (product) url += `&product_type=${product}`;
    if (region) url += `&region=${region}`;
    
    try {
        const response = await utils.apiRequest(url);
        // 更新表格...（代码省略）
    } catch (error) {
        console.error('筛选价格失败:', error);
    }
}

// 处理退出登录
function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        utils.clearAll();
        window.location.href = 'login.html';
    }
}

// 处理升级会员
async function handleUpgrade() {
    if (confirm('确定要升级为付费会员吗？')) {
        try {
            const response = await utils.apiRequest(API_ENDPOINTS.upgrade, {
                method: 'POST'
            });
            
            if (response.success) {
                utils.showAlert('升级成功！', 'success');
                // 更新用户信息
                const userInfo = utils.getUserInfo();
                userInfo.user_type = 'paid';
                utils.setUserInfo(userInfo);
                
                // 刷新页面
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        } catch (error) {
            utils.showAlert('升级失败：' + error.message, 'danger');
        }
    }
}

// 查看资讯详情
function viewNewsDetail(newsId) {
    // 记录查看行为
    utils.recordBehavior('view', { 
        content_type: 'news', 
        content_id: newsId,
        duration: 30 
    });
    
    // TODO: 显示详情模态框
    alert('查看资讯详情功能开发中...');
} 
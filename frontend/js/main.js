// 主页JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // 平滑滚动
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 导航栏滚动效果
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
    });
    
    // 动画效果
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // 为卡片添加动画
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
});

// AI助手配置
const AI_ASSISTANTS = {
    customer: {
        id: '9714d9bc-31ca-40b5-a720-4329f5fc4af7',
        token: 'e0dc8833077b48669a04ad4a70a7ebe2',
        name: '客服助手'
    },
    news: {
        id: '158ab70e-2996-4cce-9822-6f8195a7cfa5',
        token: '9bc6008decb94efeaee65dd076aab5e8',
        name: '资讯助手'
    },
    trading: {
        id: '1e72acc1-43a8-4cda-8d54-f409c9c5d5ed',
        token: '18703d14357040c88f32ae5e4122c2d6',
        name: '交易助手'
    }
};

// 打开AI助手
function openAiAssistant(assistantType) {
    const assistant = AI_ASSISTANTS[assistantType];
    if (!assistant) {
        alert('未找到对应的AI助手');
        return;
    }
    
    // 获取用户选择的身份
    const userCompany = document.getElementById('userCompany').value;
    
    // 创建AI助手窗口
    const aiWindow = window.open('', '_blank', 'width=400,height=600,scrollbars=yes,resizable=yes');
    
    // 设置窗口标题
    aiWindow.document.title = assistant.name;
    
    // 创建AI助手页面内容
    const aiContent = `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${assistant.name}</title>
        <style>
            body { 
                margin: 0; 
                padding: 20px; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                background: #f5f5f5;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .user-info {
                background: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                font-size: 14px;
                border-left: 4px solid #2196f3;
            }
            #bot-container {
                height: 500px;
                border: none;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h3>${assistant.name}</h3>
            <p>为您提供专业的${assistantType === 'customer' ? '客服' : assistantType === 'news' ? '资讯' : '交易'}服务</p>
        </div>
        ${userCompany ? `
        <div class="user-info">
            <strong>当前身份:</strong> ${userCompany}
            <br><small>AI助手将基于您的身份提供个性化服务</small>
        </div>
        ` : ''}
        <div id="bot-container"></div>
        
        <script>
            // AI助手初始化脚本
            (function* botLoader() {
                const botConfig = new Proxy({
                    id: '${assistant.id}',
                    token: '${assistant.token}',
                    size: 'normal',
                    theme: 'light',
                    host: 'https://ai.wiseocean.cn',
                    ${userCompany ? `userTag: '${userCompany}',` : ''}
                    container: 'bot-container'
                }, {
                    get: (target, prop) => {
                        console.debug('[Bot Config]', prop, target[prop]);
                        return target[prop];
                    }
                });

                yield new Promise(resolve => {
                    const inject = document.createElement('script');
                    Object.assign(inject, {
                        src: 'https://ai.wiseocean.cn/bot/robot.js',
                        onload: () => {
                            requestAnimationFrame(() => {
                                WiseBotInit(botConfig);
                                resolve();
                            });
                        }
                    });
                    document.body.appendChild(inject);
                });
            })().next();
        </script>
    </body>
    </html>
    `;
    
    // 写入内容到新窗口
    aiWindow.document.write(aiContent);
    aiWindow.document.close();
    
    // 记录用户行为（如果有相关API）
    if (typeof utils !== 'undefined' && utils.recordBehavior) {
        utils.recordBehavior('ai_assistant_opened', {
            assistant_type: assistantType,
            user_company: userCompany,
            timestamp: new Date().toISOString()
        });
    }
} 
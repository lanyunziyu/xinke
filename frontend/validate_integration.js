#!/usr/bin/env node

/**
 * Vue前端与后端API集成验证脚本
 * 模拟前端store的API调用流程，验证整个系统的工作状态
 */

const baseURL = 'http://localhost:8000';

console.log('🚀 开始验证Vue前端与后端API的集成状态...\n');

// 测试结果统计
const results = {
    passed: 0,
    failed: 0,
    total: 0
};

function logTest(name, status, details = '') {
    results.total++;
    const icon = status ? '✅' : '❌';
    const statusText = status ? 'PASS' : 'FAIL';

    if (status) results.passed++;
    else results.failed++;

    console.log(`${icon} [${statusText}] ${name}`);
    if (details) {
        console.log(`   ${details}`);
    }
    console.log('');
}

// 1. 验证后端服务健康状态
async function testBackendHealth() {
    try {
        const response = await fetch(`${baseURL}/health`);
        const data = await response.json();

        if (response.ok && data.status === 'healthy' && data.agent_initialized) {
            logTest(
                '后端API健康检查',
                true,
                `Agent已初始化，工具数量: ${data.tools_count}`
            );
            return true;
        } else {
            logTest('后端API健康检查', false, `状态异常: ${JSON.stringify(data)}`);
            return false;
        }
    } catch (error) {
        logTest('后端API健康检查', false, `连接失败: ${error.message}`);
        return false;
    }
}

// 2. 验证统一聊天接口（非流式）
async function testUnifiedChatAPI() {
    try {
        const testMessage = "我想在北京朝阳区买首套房，预算800万，需要了解购房政策";

        const response = await fetch(`${baseURL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: testMessage,
                stream: false,
                max_iterations: 5
            })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success' && data.response) {
            logTest(
                '统一聊天接口（非流式）',
                true,
                `会话ID: ${data.conversation_id}, 响应长度: ${data.response.length}字符, 迭代次数: ${data.iterations}`
            );
            return data.conversation_id; // 返回会话ID供后续测试使用
        } else {
            logTest('统一聊天接口（非流式）', false, `请求失败: ${JSON.stringify(data)}`);
            return null;
        }
    } catch (error) {
        logTest('统一聊天接口（非流式）', false, `连接失败: ${error.message}`);
        return null;
    }
}

// 3. 验证流式聊天接口
async function testStreamingChatAPI() {
    try {
        const response = await fetch(`${baseURL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: "请简单介绍北京购房的基本要求",
                stream: true,
                max_iterations: 3
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let events = [];
        let fullMessage = '';
        let conversationId = '';

        // 解析SSE流
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // 保留可能不完整的最后一行

            let currentEvent = null;
            for (const line of lines) {
                const trimmedLine = line.trim();

                if (trimmedLine.startsWith('event: ')) {
                    currentEvent = trimmedLine.slice(7);
                } else if (trimmedLine.startsWith('data: ')) {
                    if (currentEvent) {
                        try {
                            const data = JSON.parse(trimmedLine.slice(6));
                            events.push({ type: currentEvent, data });

                            // 累积消息内容
                            if (currentEvent === 'message' && data.content) {
                                fullMessage += data.content;
                            }

                            // 提取会话ID
                            if (currentEvent === 'complete' && data.conversation_id) {
                                conversationId = data.conversation_id;
                            }
                        } catch (e) {
                            console.warn(`   ⚠️  SSE数据解析失败: ${e.message}`);
                        }
                    }
                }
            }
        }

        const messageEvents = events.filter(e => e.type === 'message');
        const completeEvents = events.filter(e => e.type === 'complete');

        if (messageEvents.length > 0 && completeEvents.length > 0) {
            logTest(
                '流式聊天接口（SSE）',
                true,
                `接收到 ${events.length} 个事件，消息长度: ${fullMessage.length}字符，会话ID: ${conversationId}`
            );
            return conversationId;
        } else {
            logTest('流式聊天接口（SSE）', false, `事件数据异常: ${events.length} 个事件`);
            return null;
        }

    } catch (error) {
        logTest('流式聊天接口（SSE）', false, `连接失败: ${error.message}`);
        return null;
    }
}

// 4. 验证会话管理接口
async function testSessionManagement() {
    try {
        // 获取会话列表
        const response = await fetch(`${baseURL}/sessions`);
        const data = await response.json();

        if (response.ok && data.sessions !== undefined) {
            logTest(
                '会话管理接口',
                true,
                `当前活跃会话: ${data.total} 个`
            );
            return data.sessions;
        } else {
            logTest('会话管理接口', false, `请求失败: ${JSON.stringify(data)}`);
            return null;
        }
    } catch (error) {
        logTest('会话管理接口', false, `连接失败: ${error.message}`);
        return null;
    }
}

// 5. 验证会话重置功能
async function testSessionReset() {
    try {
        const response = await fetch(`${baseURL}/reset`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            logTest(
                '会话重置功能',
                true,
                data.message
            );
            return true;
        } else {
            logTest('会话重置功能', false, `重置失败: ${JSON.stringify(data)}`);
            return false;
        }
    } catch (error) {
        logTest('会话重置功能', false, `连接失败: ${error.message}`);
        return false;
    }
}

// 6. 验证前端服务状态
async function testFrontendService() {
    try {
        const response = await fetch('http://localhost:3002/', {
            method: 'HEAD' // 只获取头部信息
        });

        if (response.ok) {
            logTest(
                '前端开发服务',
                true,
                `Vue应用运行在 http://localhost:3002/`
            );
            return true;
        } else {
            logTest('前端开发服务', false, `HTTP ${response.status}: ${response.statusText}`);
            return false;
        }
    } catch (error) {
        logTest('前端开发服务', false, `连接失败: ${error.message}`);
        return false;
    }
}

// 7. 模拟前端Store工作流程
async function testStoreWorkflow() {
    console.log('🔄 模拟Vue Store工作流程...\n');

    try {
        // 模拟用户提交输入
        const userInput = "我是首次购房，想在北京买房，预算1000万，请帮我分析需要准备多少资金";

        console.log(`📝 用户输入: ${userInput}`);
        console.log('📡 发送到 sendMessageStream...\n');

        // 调用流式接口（模拟 store.sendMessageStream）
        const response = await fetch(`${baseURL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userInput,
                stream: true,
                max_iterations: 10
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let conversationHistory = [
            { role: 'user', content: userInput, timestamp: new Date().toISOString() }
        ];
        let streamingMessage = '';
        let toolCalls = [];

        console.log('🔄 开始接收流式事件...\n');

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            let currentEvent = null;
            for (const line of lines) {
                const trimmedLine = line.trim();

                if (trimmedLine.startsWith('event: ')) {
                    currentEvent = trimmedLine.slice(7);
                } else if (trimmedLine.startsWith('data: ')) {
                    if (currentEvent) {
                        try {
                            const data = JSON.parse(trimmedLine.slice(6));

                            // 模拟store.handleStreamEvent逻辑
                            switch (currentEvent) {
                                case 'message':
                                    streamingMessage += data.content || '';
                                    console.log(`💬 接收消息片段: ${(data.content || '').substring(0, 50)}...`);
                                    break;

                                case 'tool_call':
                                    const toolCall = {
                                        id: Date.now(),
                                        name: data.name || '未知工具',
                                        status: 'running',
                                        message: `正在调用 ${data.name || '工具'}`
                                    };
                                    toolCalls.push(toolCall);
                                    console.log(`🔧 工具调用: ${toolCall.message}`);
                                    break;

                                case 'complete':
                                    // 完成，添加到对话历史
                                    conversationHistory.push({
                                        role: 'assistant',
                                        content: streamingMessage,
                                        timestamp: new Date().toISOString()
                                    });

                                    console.log(`✅ 对话完成！`);
                                    console.log(`📋 会话ID: ${data.conversation_id}`);
                                    console.log(`📊 消息总长度: ${streamingMessage.length}字符`);
                                    console.log(`🛠️  工具调用次数: ${toolCalls.length}`);

                                    // 检查是否包含报告内容
                                    const isReport = streamingMessage.includes('购房资金方案报告') ||
                                                   streamingMessage.includes('总成本概览');

                                    if (isReport) {
                                        console.log(`📄 检测到完整报告，切换到结果展示状态`);
                                    }

                                    break;

                                case 'error':
                                    console.log(`❌ 错误事件: ${data.error || data.message}`);
                                    break;
                            }
                        } catch (e) {
                            console.log(`⚠️  事件解析失败: ${e.message}`);
                        }
                    }
                }
            }
        }

        logTest(
            'Vue Store工作流程模拟',
            true,
            `成功模拟完整的用户交互流程，对话历史: ${conversationHistory.length} 条消息`
        );

        return true;

    } catch (error) {
        logTest('Vue Store工作流程模拟', false, `流程失败: ${error.message}`);
        return false;
    }
}

// 主测试函数
async function runIntegrationTests() {
    console.log('=' * 80);
    console.log('🎯 Vue前端与后端API集成验证');
    console.log('=' * 80);
    console.log('');

    // 运行所有测试
    const backendOK = await testBackendHealth();
    const frontendOK = await testFrontendService();

    if (!backendOK) {
        console.log('❌ 后端服务异常，无法继续测试API功能');
        return;
    }

    const conversationId1 = await testUnifiedChatAPI();
    const conversationId2 = await testStreamingChatAPI();
    const sessions = await testSessionManagement();
    await testStoreWorkflow();
    await testSessionReset();

    // 输出测试总结
    console.log('=' * 80);
    console.log('📊 测试结果总结');
    console.log('=' * 80);
    console.log(`✅ 通过: ${results.passed}/${results.total}`);
    console.log(`❌ 失败: ${results.failed}/${results.total}`);
    console.log(`📈 成功率: ${(results.passed / results.total * 100).toFixed(1)}%`);

    if (results.failed === 0) {
        console.log('');
        console.log('🎉 所有测试通过！Vue前端与后端API集成完全正常');
        console.log('🌟 系统已准备就绪，可以正常使用');
        console.log('');
        console.log('🚀 访问地址:');
        console.log('   前端应用: http://localhost:3002/');
        console.log('   测试页面: file://test_frontend.html');
        console.log('   API文档:  http://localhost:8000/docs');
    } else {
        console.log('');
        console.log('⚠️  发现问题，建议检查失败的测试项目');
    }

    console.log('');
}

// 运行测试
runIntegrationTests().catch(error => {
    console.error('❌ 集成测试运行失败:', error);
    process.exit(1);
});
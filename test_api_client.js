// Simple Node.js test for API integration
const baseURL = 'http://localhost:8000';

// Test health endpoint
async function testHealth() {
    console.log('\n🔍 Testing Health Endpoint...');
    try {
        const response = await fetch(`${baseURL}/health`);
        const data = await response.json();

        if (response.ok && data.status === 'healthy') {
            console.log('✅ Health check passed');
            console.log(`   Status: ${data.status}`);
            console.log(`   Agent initialized: ${data.agent_initialized}`);
            console.log(`   Tools count: ${data.tools_count}`);
        } else {
            console.log('❌ Health check failed');
            console.log(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        console.log(`❌ Health check error: ${error.message}`);
    }
}

// Test non-streaming chat
async function testChat() {
    console.log('\n🔍 Testing Non-streaming Chat...');
    try {
        const response = await fetch(`${baseURL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: '我想在北京朝阳区买首套房，预算800万，需要了解政策和资金准备',
                stream: false,
                max_iterations: 5
            })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            console.log('✅ Non-streaming chat success');
            console.log(`   Conversation ID: ${data.conversation_id}`);
            console.log(`   Iterations: ${data.iterations}`);
            console.log(`   Response length: ${data.response?.length || 0} chars`);
            console.log(`   First 200 chars: ${data.response?.substring(0, 200)}...`);
        } else {
            console.log('❌ Chat failed');
            console.log(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        console.log(`❌ Chat error: ${error.message}`);
    }
}

// Test streaming chat
async function testStreamingChat() {
    console.log('\n🔍 Testing Streaming Chat...');
    try {
        const response = await fetch(`${baseURL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: '请简单介绍一下北京购房政策',
                stream: true,
                max_iterations: 3
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        console.log('✅ Streaming connection established');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = null;
        let messageCount = 0;
        let fullMessage = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                const trimmedLine = line.trim();

                if (trimmedLine.startsWith('event: ')) {
                    currentEvent = trimmedLine.slice(7);
                } else if (trimmedLine.startsWith('data: ')) {
                    if (currentEvent) {
                        try {
                            const data = JSON.parse(trimmedLine.slice(6));

                            switch (currentEvent) {
                                case 'message':
                                    messageCount++;
                                    fullMessage += data.content || data.message || '';
                                    break;
                                case 'complete':
                                    console.log(`   Events received: ${messageCount} message events`);
                                    console.log(`   Full message length: ${fullMessage.length} chars`);
                                    console.log(`   Conversation ID: ${data.conversation_id || 'N/A'}`);
                                    break;
                                case 'error':
                                    console.log(`   ❌ Stream error: ${data.error || data.message}`);
                                    break;
                            }
                        } catch (e) {
                            console.log(`   ⚠️  Parse error: ${e.message}`);
                        }
                    }
                }
            }
        }

        console.log('✅ Streaming completed successfully');

    } catch (error) {
        console.log(`❌ Streaming error: ${error.message}`);
    }
}

// Test session management
async function testSessions() {
    console.log('\n🔍 Testing Session Management...');
    try {
        const response = await fetch(`${baseURL}/sessions`);
        const data = await response.json();

        if (response.ok) {
            console.log('✅ Session list retrieved');
            console.log(`   Total sessions: ${data.total}`);
            console.log(`   Session count: ${data.sessions?.length || 0}`);
        } else {
            console.log('❌ Session retrieval failed');
            console.log(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        console.log(`❌ Sessions error: ${error.message}`);
    }
}

// Main test runner
async function runTests() {
    console.log('🚀 Starting API Integration Tests...');
    console.log('=' * 50);

    await testHealth();
    await testChat();
    await testStreamingChat();
    await testSessions();

    console.log('\n✅ All tests completed!');
    console.log('=' * 50);
}

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
    runTests().catch(console.error);
}
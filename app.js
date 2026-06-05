document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements - Screens
    const loginScreen = document.getElementById("loginScreen");
    const mainAppScreen = document.getElementById("mainAppScreen");
    
    // DOM Elements - Login Form
    const loginForm = document.getElementById("loginForm");
    const passwordToggle = document.getElementById("passwordToggle");
    const loginPassword = document.getElementById("loginPassword");
    const touchIdBtn = document.getElementById("touchIdBtn");
    const faceIdBtn = document.getElementById("faceIdBtn");

    // DOM Elements - Navigation and Header
    const menuItems = document.querySelectorAll(".menu-item");
    const viewPanels = document.querySelectorAll(".view-panel");
    const viewTitle = document.getElementById("viewTitle");
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    
    // DOM Elements - Chat Components
    const chatMessages = document.getElementById("chatMessages");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const typingIndicator = document.getElementById("typingIndicator");
    const newChatBtn = document.getElementById("newChatBtn");
    const recentChatsList = document.getElementById("recentChatsList");
    const suggestGrid = document.querySelector(".suggest-grid");

    // DOM Elements - Sub-views click targets
    const schemeCards = document.querySelectorAll(".scheme-card");

    // Server API Base URL
    const API_BASE = window.location.origin;

    // Recent Chats Mock Data
    const mockRecentChats = [
        { id: 1, title: "Large & Midcap Expense Ratio", query: "What is the expense ratio of the Motilal Oswal Large and Midcap Fund?", time: "2 hours ago" },
        { id: 2, title: "Contra Fund Exit Load Details", query: "What is the exit load of the Motilal Oswal Contra Fund?", time: "Yesterday" },
        { id: 3, title: "Digital India Manager Name", query: "Who are the fund managers of the Motilal Oswal Digital India Fund?", time: "Oct 12, 2023" },
        { id: 4, title: "ELSS 3 Year Tax Lock-in", query: "What is the lock-in period of Motilal Oswal Most Focused Long Term Fund?", time: "Oct 10, 2023" }
    ];

    // ==========================================
    // 1. MOCK LOGIN FLOWS
    // ==========================================
    
    // Toggle Password visibility
    passwordToggle.addEventListener("click", () => {
        if (loginPassword.type === "password") {
            loginPassword.type = "text";
            passwordToggle.textContent = "🙈";
        } else {
            loginPassword.type = "password";
            passwordToggle.textContent = "👁️";
        }
    });

    const triggerLoginTransition = () => {
        // Smooth transition: fade out login, fade in dashboard
        loginScreen.style.opacity = 0;
        loginScreen.style.transform = "scale(0.98)";
        
        setTimeout(() => {
            loginScreen.classList.add("hidden");
            mainAppScreen.classList.remove("hidden");
            mainAppScreen.style.opacity = 0;
            
            // Trigger browser reflow
            mainAppScreen.offsetHeight; 
            
            mainAppScreen.style.transition = "opacity 0.4s ease";
            mainAppScreen.style.opacity = 1;
            
            // Focus input immediately after login
            chatInput.focus();
        }, 300);
    };

    // Form Submit login
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        triggerLoginTransition();
    });

    // Biometric Button clicks
    touchIdBtn.addEventListener("click", triggerLoginTransition);
    faceIdBtn.addEventListener("click", triggerLoginTransition);

    // ==========================================
    // 2. SPA PANEL ROUTING
    // ==========================================
    
    const viewNames = {
        chatView: "Wealth Assistant",
        exploreView: "Explore Mutual Funds",
        profileView: "Compliance Profile"
    };

    menuItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetViewId = item.getAttribute("data-view");
            
            // Update Active Menu state
            menuItems.forEach(mi => mi.classList.remove("active"));
            item.classList.add("active");
            
            // Switch Panel Visibility
            viewPanels.forEach(panel => {
                if (panel.id === targetViewId) {
                    panel.classList.remove("hidden");
                } else {
                    panel.classList.add("hidden");
                }
            });

            // Update Header Title
            viewTitle.textContent = viewNames[targetViewId] || "Groww";
        });
    });

    // ==========================================
    // 3. THEME MANAGEMENT
    // ==========================================
    const savedTheme = localStorage.getItem("app-theme") || "dark-theme";
    document.body.className = savedTheme;
    updateThemeToggleBtnStyle(savedTheme);

    themeToggleBtn.addEventListener("click", () => {
        if (document.body.classList.contains("dark-theme")) {
            document.body.classList.replace("dark-theme", "light-theme");
            localStorage.setItem("app-theme", "light-theme");
            updateThemeToggleBtnStyle("light-theme");
        } else {
            document.body.classList.replace("light-theme", "dark-theme");
            localStorage.setItem("app-theme", "dark-theme");
            updateThemeToggleBtnStyle("dark-theme");
        }
    });

    function updateThemeToggleBtnStyle(theme) {
        if (theme === "light-theme") {
            themeToggleBtn.innerHTML = `<span class="toggle-icon">🌙</span>`;
        } else {
            themeToggleBtn.innerHTML = `<span class="toggle-icon">☀️</span>`;
        }
    }

    // ==========================================
    // 4. RECENT CHATS & QUESTION CHIPS
    // ==========================================
    
    // Generate Recent list items
    const populateRecentChats = () => {
        recentChatsList.innerHTML = "";
        mockRecentChats.forEach(chat => {
            const btn = document.createElement("button");
            btn.className = "recent-chat-item";
            btn.innerHTML = `
                <span class="recent-chat-icon">💬</span>
                <div class="recent-chat-text">
                    <span class="recent-chat-title">${chat.title}</span>
                    <span class="recent-chat-time">${chat.time}</span>
                </div>
            `;
            btn.addEventListener("click", () => {
                // Submit this query to the chat workspace
                switchToChatView();
                sendMessage(chat.query);
            });
            recentChatsList.appendChild(btn);
        });
    };
    populateRecentChats();

    // Suggested Chips click
    if (suggestGrid) {
        const suggestChips = suggestGrid.querySelectorAll(".suggest-chip");
        suggestChips.forEach(chip => {
            chip.addEventListener("click", () => {
                const query = chip.getAttribute("data-query");
                sendMessage(query);
            });
        });
    }

    // Scheme Explorer card click-to-ask
    schemeCards.forEach(card => {
        card.addEventListener("click", () => {
            const query = card.getAttribute("data-query");
            switchToChatView();
            sendMessage(query);
        });
    });

    const switchToChatView = () => {
        // Toggle Active state on sidebar Chat menu
        menuItems.forEach(mi => {
            if (mi.getAttribute("data-view") === "chatView") {
                mi.classList.add("active");
            } else {
                mi.classList.remove("active");
            }
        });

        // Hide other views, show chat
        viewPanels.forEach(panel => {
            if (panel.id === "chatView") {
                panel.classList.remove("hidden");
            } else {
                panel.classList.add("hidden");
            }
        });

        viewTitle.textContent = viewNames["chatView"];
    };

    // New Chat resets the conversation
    newChatBtn.addEventListener("click", () => {
        switchToChatView();
        
        // Retain welcome message but clear dynamic history
        chatMessages.innerHTML = `
            <div class="message-wrapper bot">
                <div class="message-bubble">
                    <p><strong>Conversation Reset.</strong> Ask me anything about Motilal Oswal mutual fund schemes.</p>
                </div>
                <div class="message-footer">Groww AI Assistant</div>
            </div>
            
            <div class="suggest-questions-wrapper" id="suggestQuestions">
                <h4 class="suggest-title">Suggested Mutual Fund Questions</h4>
                <div class="suggest-grid">
                    <button class="suggest-chip" data-query="What is the expense ratio of the Motilal Oswal Large and Midcap Fund?">
                        📊 Expense Ratio: Large & Midcap Fund
                    </button>
                    <button class="suggest-chip" data-query="Who is the fund manager of the Motilal Oswal Contra Fund?">
                        👨‍💼 Managers: Contra Fund
                    </button>
                    <button class="suggest-chip" data-query="What is the exit load of the Motilal Oswal Active Momentum Fund?">
                        ⚖️ Exit Load: Active Momentum
                    </button>
                    <button class="suggest-chip" data-query="Should I invest in the Motilal Oswal Large and Midcap Fund?">
                        🛡️ Investment Recommendation (Advisory Check)
                    </button>
                </div>
            </div>
        `;
        
        // Reconnect suggested chips handlers
        const newChips = chatMessages.querySelectorAll(".suggest-chip");
        newChips.forEach(chip => {
            chip.addEventListener("click", () => {
                sendMessage(chip.getAttribute("data-query"));
            });
        });
        
        chatInput.value = "";
        chatInput.focus();
    });

    // ==========================================
    // 5. CHAT ENGINE CLIENT INTEGRATION
    // ==========================================
    
    // Markdown Parser
    function parseMarkdown(text) {
        let parsed = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        parsed = parsed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        return parsed;
    }

    // Append Chat Bubble
    function appendMessage(role, text, footer = "", citations = []) {
        const wrapper = document.createElement("div");
        wrapper.className = `message-wrapper ${role}`;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = parseMarkdown(text);
        wrapper.appendChild(bubble);

        // Add citation if available
        if (citations && citations.length > 0) {
            const citationDiv = document.createElement("div");
            citationDiv.className = "citation-container";
            citationDiv.innerHTML = `📚 Source: <a href="${citations[0]}" target="_blank" rel="noopener noreferrer">Groww official source page</a>`;
            wrapper.appendChild(citationDiv);
        }

        // Add footer date
        if (footer) {
            const footerDiv = document.createElement("div");
            footerDiv.className = "message-footer";
            footerDiv.textContent = footer;
            wrapper.appendChild(footerDiv);
        }

        chatMessages.appendChild(wrapper);
        scrollToBottom();
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 50);
    }

    // Send Message
    async function sendMessage(messageText) {
        if (!messageText) return;
        messageText = messageText.trim();
        if (!messageText) return;

        // Hide suggested questions block from view once chatting begins
        const suggestQuestions = document.getElementById("suggestQuestions");
        if (suggestQuestions) {
            suggestQuestions.remove();
        }

        // Append User Message bubble
        appendMessage("user", messageText);
        
        // Clear and focus input
        chatInput.value = "";
        chatInput.focus();

        // Show typing indicator
        typingIndicator.classList.remove("hidden");
        scrollToBottom();

        try {
            const response = await fetch(`${API_BASE}/api/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: messageText })
            });

            typingIndicator.classList.add("hidden");

            if (response.ok) {
                const data = await response.json();
                appendMessage("bot", data.answer, data.footer, data.citations);
            } else {
                const errorData = await response.json();
                appendMessage("bot", `⚠️ Error: ${errorData.detail || "Unable to get response from server."}`);
            }
        } catch (error) {
            typingIndicator.classList.add("hidden");
            appendMessage("bot", "⚠️ Error: Connection to the Groww FAQ server failed. Please check if backend is running.");
            console.error("Fetch error:", error);
        }
    }

    // Input form submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        sendMessage(text);
    });
});

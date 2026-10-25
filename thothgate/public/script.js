
window.onload = function() {
    const loader = document.getElementById('loader');
    // const content = document.getElementById('content');

    loader.style.display = 'none';

    // content.style.display = 'block';
};
// Ensure profile edit buttons work even if script loads before DOM
document.addEventListener('DOMContentLoaded', function() {
    var saveBtn = document.querySelector('.save-btn');
    var cancelBtn = document.querySelector('.cancel-btn');
    var editBtn = document.querySelector('.edit-profile-btn');
    if (saveBtn) saveBtn.onclick = saveProfile;
    if (cancelBtn) cancelBtn.onclick = cancelEdit;
    if (editBtn) editBtn.onclick = toggleEditMode;
});
let isLoggedIn = false;
let currentUser = null;
let currentTheme = localStorage.getItem('thuthGateTheme') || 'light';
let currentLanguage = localStorage.getItem('thuthGateLanguage') || 'en';


document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    checkAuthStatus();
    initializeTheme();
    initializeLanguage();
    addEventListeners();
    initializePageFunctionality();
}

// Check authentication status
function checkAuthStatus() {
    const token = localStorage.getItem('thuthGateToken');
    if (token) {
        isLoggedIn = true;
        currentUser = JSON.parse(localStorage.getItem('thuthGateUser'));
        updateUIForLoggedInUser();
    } else {
        isLoggedIn = false;
        currentUser = null;
        updateUIForLoggedOutUser();
    }
}

// Add event listeners
function addEventListeners() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // const imageInput = document.getElementById('imageInput');
    // if (imageInput) {
    //     imageInput.addEventListener('change', handleImageUpload);
    // }

    const themeSwitcher = document.getElementById('themeSwitcher');
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', toggleTheme);
    }



    initializeMobileSidebar();

    addSmoothScrolling();
}


function initializePageFunctionality() {
    const currentPage = getCurrentPage();

    switch (currentPage) {
        case 'login':

            break;
        case 'register':

            break;
        case 'home':
            initializeHomePage();
            break;
        case 'profile':
            initializeProfilePage();
            break;
        case 'chat':
            initializeChatPage();
            break;
    }
}

// Get current page
function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('index.html') || path === '/' || path === '') {
        return 'login';
    } else if (path.includes('register.html')) {
        return 'register';
    } else if (path.includes('home.html')) {
        return 'home';
    } else if (path.includes('profile.html')) {
        return 'profile';
    } else if (path.includes('chat.html')) {
        return 'chat';
    }
    return 'login';
}


function handleLogin(event) {
    event.preventDefault();
    window.location.href = 'home.html';
}

function handleRegister(event) {
    event.preventDefault();
    showMessage('Registration functionality is disabled. No backend simulation.', 'error');
}

// ...existing code...

// Update UI for logged in user
function updateUIForLoggedInUser() {
    if (currentUser) {
        // Update profile information if on profile page
        updateProfileDisplay();
    }
}

// Update UI for logged out user
function updateUIForLoggedOutUser() {
    // Redirect to login if trying to access protected pages
    const currentPage = getCurrentPage();
    if (currentPage !== 'login' && currentPage !== 'register') {
        window.location.href = 'index.html';
    }
}

// Initialize home page
function initializeHomePage() {
    // Add scroll animations
    addScrollAnimations();


    initializeCourseInteractions();
}

// Initialize profile page
function initializeProfilePage() {
    // Load user data
    if (currentUser) {
        updateProfileDisplay();
    }
}

// Update profile display
function updateProfileDisplay() {
    if (!currentUser) return;

    // Update profile image
    const profileImage = document.getElementById('profileImage');
    if (profileImage) {
        profileImage.src = currentUser.avatar;
    }

    // Update profile details
    const studentName = document.getElementById('studentName');
    const studentEmail = document.getElementById('studentEmail');

    if (studentName) {
        studentName.textContent = currentUser.name;
    }

    if (studentEmail) {
        studentEmail.textContent = currentUser.email;
    }
}

// Toggle edit mode for profile
function toggleEditMode() {
    const nameSpan = document.getElementById('studentName');
    const emailSpan = document.getElementById('studentEmail');
    const nameInput = document.getElementById('nameInput');
    const emailInput = document.getElementById('emailInput');
    const imageUpload = document.getElementById('imageUpload');
    const profileActions = document.getElementById('profileActions');
    const editBtn = document.querySelector('.edit-profile-btn');

    if (nameSpan && emailSpan && nameInput && emailInput) {
        if (nameSpan.style.display !== 'none') {
            // Switch to edit mode
            nameSpan.style.display = 'none';
            emailSpan.style.display = 'none';
            nameInput.style.display = 'inline-block';
            emailInput.style.display = 'inline-block';
            imageUpload.style.display = 'block';
            profileActions.style.display = 'flex';
            editBtn.textContent = 'Cancel Edit';
            editBtn.onclick = cancelEdit;
        }
    }
}

// Cancel profile editing
function cancelEdit() {
    const nameSpan = document.getElementById('studentName');
    const emailSpan = document.getElementById('studentEmail');
    const nameInput = document.getElementById('nameInput');
    const emailInput = document.getElementById('emailInput');
    const imageUpload = document.getElementById('imageUpload');
    const profileActions = document.getElementById('profileActions');
    const editBtn = document.querySelector('.edit-profile-btn');

    // Always restore view mode, even if currentUser is null
    if (nameSpan) nameSpan.style.display = 'inline';
    if (emailSpan) emailSpan.style.display = 'inline';
    if (nameInput) nameInput.style.display = 'none';
    if (emailInput) emailInput.style.display = 'none';
    if (imageUpload) imageUpload.style.display = 'none';
    if (profileActions) profileActions.style.display = 'none';
    if (editBtn) {
        editBtn.textContent = 'Edit Profile';
        editBtn.onclick = toggleEditMode;
    }

    // Optionally reset input values if user data exists
    if (currentUser && nameInput && emailInput) {
        nameInput.value = currentUser.name;
        emailInput.value = currentUser.email;
    }
}

function saveProfile() {
    const nameInput = document.getElementById('nameInput');
    const emailInput = document.getElementById('emailInput');
    if (nameInput && emailInput) {
        const newName = nameInput.value.trim();
        const newEmail = emailInput.value.trim();
        if (!newName || !newEmail) {
            showMessage('Please fill in all fields.', 'error');
            return;
        }
        if (!isValidEmail(newEmail)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        // Update local storage
        if (currentUser) {
            currentUser.name = newName;
            currentUser.email = newEmail;
            localStorage.setItem('thuthGateUser', JSON.stringify(currentUser));
            updateProfileDisplay();
        }
        showMessage('Profile updated successfully!', 'success');
    }
    // Always exit edit mode after save attempt
    cancelEdit();
}

// Handle image upload
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {

        if (!file.type.startsWith('image/')) {
            showMessage('Please select an image file.', 'error');
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showMessage('Image size should be less than 5MB.', 'error');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const profileImage = document.getElementById('profileImage');
            if (profileImage) {
                profileImage.src = e.target.result;
                // Update current user avatar
                currentUser.avatar = e.target.result;
                localStorage.setItem('thuthGateUser', JSON.stringify(currentUser));
            }
        };
        reader.readAsDataURL(file);

        showMessage('Profile picture updated!', 'success');
    }
}

// Add smooth scrolling
function addSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.course-card, .teacher-card, .enrolled-course-card, .stat-card');
    animatedElements.forEach(el => observer.observe(el));
}


function initializeCourseInteractions() {
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add course interaction logic here
            console.log('Course clicked:', this.querySelector('h3').textContent);
        });
    });
}


function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    // Insert message
    const container = document.querySelector('.container') || document.querySelector('.login-container');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utility function to get URL parameters
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Utility function to format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Theme Management
function initializeTheme() {
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcon();
    }
}

function toggleTheme() {
    if (currentTheme === 'light') {
        currentTheme = 'dark';
        document.body.classList.add('dark-mode');
    } else {
        currentTheme = 'light';
        document.body.classList.remove('dark-mode');
    }

    localStorage.setItem('thuthGateTheme', currentTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Language Management
async function initializeLanguage() {
    await loadTranslations();

    if (currentLanguage === "ar") {
        document.documentElement.setAttribute("dir", "rtl");
        document.documentElement.setAttribute("lang", "ar");
    } else {
        document.documentElement.setAttribute("dir", "ltr");
        document.documentElement.setAttribute("lang", "en");
    }

    applyTranslations(currentLanguage);
    updateLanguageText();
}


function toggleLanguage() {
    currentLanguage = currentLanguage === "en" ? "ar" : "en";
    localStorage.setItem("thuthGateLanguage", currentLanguage);
    initializeLanguage(); // reload + apply translations
    updateLanguageText();
}

function updateLanguageText() {
    const languageText = document.querySelector('.language-text');
    if (languageText) {
        languageText.textContent = currentLanguage === 'ar' ? 'AR' : 'EN';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const languageSwitcher = document.getElementById('languageSwitcher');
    if (languageSwitcher) {
        languageSwitcher.addEventListener('click', toggleLanguage);
    }
    initializeLanguage();
});

function translateTextContent(translations) {
    document.querySelectorAll('*').forEach(el => {
        el.childNodes.forEach(node => {
            if (node.nodeType === 3) { // text node
                const normalized = normalizeText(node.textContent);
                if (translations[normalized]) {
                    node.textContent = translations[normalized];
                }
            }
        });
    });
}

// Replace placeholder attributes
function translatePlaceholders(translations) {
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
        const normalized = normalizeText(el.placeholder);
        if (translations[normalized]) {
            el.placeholder = translations[normalized];
        }
    });
}
// Replace button labels or input[type=button/submit] values
function translateButtons(translations) {
    document.querySelectorAll('button').forEach(el => {
        const normalized = normalizeText(el.textContent);
        if (translations[normalized]) {
            el.textContent = translations[normalized];
        }
    });
}

let translations = {};

async function loadTranslations() {
    try {
        // Find the <script> tag that loaded this file
        const scriptTag = document.querySelector('script[src*="script.js"]');
        const scriptPath = scriptTag.getAttribute("src");

        // Normalize path to where script.js actually lives
        const basePath = scriptPath.substring(0, scriptPath.lastIndexOf("/"));

        // translations.json lives next to script.js
        const response = await fetch(basePath + "/translations.json");
        translations = await response.json();
    } catch (err) {
        console.error("Failed to load translations:", err);
    }
}

function applyTranslations(lang) {
    if (!translations[lang]) return;
    translateTextContent(translations[lang]);
    translatePlaceholders(translations[lang]);
    translateButtons(translations[lang]);
}


function initializeChatPage() {
    displayUserGrade();
    loadChatMessages();
    loadOnlineStudents();
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatMessage);
    }
    // Add character count functionality
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('input', updateCharCount);
    }
    // Add emoji button functionality
    const emojiBtn = document.getElementById('emojiBtn');
    if (emojiBtn) {
        emojiBtn.addEventListener('click', showEmojiPicker);
    }
    // Simulate real-time updates
    setInterval(updateOnlineCount, 5000);
    setInterval(loadChatMessages, 10000);
}

// Display user's grade in the chat header
function displayUserGrade() {
    const gradeBadge = document.getElementById('gradeBadge');
    if (gradeBadge && currentUser) {
        const grade = currentUser.grade || '3rd Prep'; 
        gradeBadge.textContent = grade;
    }
}

// Handle chat message submission
async function handleChatMessage(event) {
    event.preventDefault();
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (!message) return;
    addChatMessage(message, 'sent');
    messageInput.value = '';
    updateCharCount();
}

// Add a chat message to the chat area
function addChatMessage(message, type = 'received', sender = 'You') {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type === 'sent' ? 'user-message' : 'other-message'}`;

    const timestamp = new Date().toLocaleTimeString();

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <img src="imgs/profile.png" alt="Student">
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${sender}</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <p>${message}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function loadChatMessages() {
    // يعمار خليه يلود مالداتا بيز
    // For now, we'll just simulate some messages <3
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages || chatMessages.children.length > 6) return; // Don't reload if messages already exist

    const sampleMessages = [
        { message: "Hi everyone! How's the math homework going?", sender: "Ahmed", type: "received" },
        { message: "I'm stuck on question 5. Anyone can help?", sender: "Fatima", type: "received" },
        { message: "I can help! The key is to use the quadratic formula.", sender: "Omar", type: "received" },
        { message: "Thanks Omar! That makes sense now.", sender: "Fatima", type: "received" }
    ];

    sampleMessages.forEach(msg => {
        addChatMessage(msg.message, msg.type, msg.sender);
    });
}

function loadOnlineStudents() {
    const onlineStudents = document.getElementById('onlineStudents');
    if (!onlineStudents) return;

    const students = [
        { name: "Ahmed Mohamed", grade: "3rd Prep" },
        { name: "Fatima Hassan", grade: "3rd Prep" },
        { name: "Omar Ali", grade: "3rd Prep" },
        { name: "Aisha Mahmoud", grade: "1st Secondary" },
        { name: "Youssef Ahmed", grade: "1st Secondary" }
    ];

    const currentGrade = currentUser?.grade || '3rd Prep';
    const gradeStudents = students.filter(student => student.grade === currentGrade);

    onlineStudents.innerHTML = '';
    gradeStudents.forEach(student => {
        const studentDiv = document.createElement('div');
        studentDiv.className = 'online-student';
        studentDiv.innerHTML = `
            <div class="online-indicator"></div>
            <span>${student.name}</span>
        `;
        onlineStudents.appendChild(studentDiv);
    });

    updateOnlineCount();
}

function updateOnlineCount() {
    const onlineCount = document.getElementById('onlineCount');
    if (onlineCount) {
        const currentGrade = currentUser?.grade || '3rd Prep';
        const count = currentGrade === '3rd Prep' ? 3 : 2; // Simulated count
        onlineCount.textContent = count;
    }
}

function updateCharCount() {
    const messageInput = document.getElementById('messageInput');
    const charCount = document.querySelector('.char-count');

    if (messageInput && charCount) {
        const count = messageInput.value.length;
        charCount.textContent = `${count}/500`;
    }
}

function showEmojiPicker() {
    let emojiPicker = document.getElementById('emojiPicker');


    if (emojiPicker) {
        if (emojiPicker.style.display === 'none') {
            emojiPicker.style.display = 'grid';
            return;
        } else {
            emojiPicker.style.display = 'none';
            return;
        }
    }

    const emojis = [
        '😊', '😄', '😃', '😁', '😆',
        '😅', '😂', '🤣', '😉', '😋',
        '😎', '😍','🥰', '😘', '😗',
        '😙', '👍', '👎','👌', '✌️',
        '🤞', '🤟', '🤘', '👊','❤️',
        '🧡', '💛', '💚', '💙', '💜',
        '🖤', '🤍', '🎉', '🎊', '📚',
        '📖', '✏️', '🖊️', '🖋️', '📌',
        '🌟', '✨', '💫', '💥', '💯'
    ];

    const emojiBtn = document.getElementById('emojiBtn');
    const messageInput = document.getElementById('messageInput');

    if (!messageInput || !emojiBtn) return;

    // emoji picker container
    const pickerElement = document.createElement('div');
    pickerElement.id = 'emojiPicker';
    pickerElement.className = 'emoji-picker';
    pickerElement.style.cssText = `
        background: white;
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 0.75rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 0.4rem;
        width: 100%;
        max-width: 100%;
        backdrop-filter: blur(10px);
        margin-bottom: 10px;
        margin-top: 10px;
        box-sizing: border-box;
            justify-items: center;

    `;

    emojis.forEach(emoji => {
        const emojiOption = document.createElement('button');
        emojiOption.textContent = emoji;
        emojiOption.className = 'emoji-option';
        emojiOption.style.cssText = `
            background: none;
            border: none;
            font-size: 1.2rem;
            padding: 0.3rem;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
        `;

        emojiOption.addEventListener('mouseenter', () => {
            emojiOption.style.background = 'rgba(212, 175, 55, 0.2)';
            emojiOption.style.transform = 'scale(1.1)';
        });

        emojiOption.addEventListener('mouseleave', () => {
            emojiOption.style.background = 'none';
            emojiOption.style.transform = 'scale(1)';
        });

        emojiOption.addEventListener('click', () => {
        const cursorPos = messageInput.selectionStart;
        const textBefore = messageInput.value.substring(0, cursorPos);
        const textAfter = messageInput.value.substring(cursorPos);
            messageInput.value = textBefore + emoji + textAfter;
            messageInput.selectionStart = messageInput.selectionEnd = cursorPos + emoji.length;
        messageInput.focus();
        updateCharCount();
        });

        pickerElement.appendChild(emojiOption);
    });

    // Add to the input container as a regular child element
    const inputContainer = document.querySelector('.chat-input-container');
    inputContainer.appendChild(pickerElement);

    // Close picker when clicking outside
    document.addEventListener('click', function closeEmojiPicker(e) {
        if (!pickerElement.contains(e.target) && e.target !== emojiBtn) {
            pickerElement.style.display = 'none';
            document.removeEventListener('click', closeEmojiPicker);
        }
    });

    // Close picker on escape key
    document.addEventListener('keydown', function escapeHandler(e) {
        if (e.key === 'Escape') {
            pickerElement.style.display = 'none';
            document.removeEventListener('keydown', escapeHandler);
        }
    });
}


// Mobile Sidebar Functionality
function initializeMobileSidebar() {
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebarThemeSwitcher = document.getElementById('sidebarThemeSwitcher');
    const sidebarLanguageSwitcher = document.getElementById('sidebarLanguageSwitcher');
    // Open sidebar
    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', () => {
            mobileSidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
            hamburgerMenu.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    function closeSidebarFunction() {
        mobileSidebar.classList.remove('open');
        sidebarOverlay.classList.remove('active');
        hamburgerMenu.classList.remove('active');
        document.body.style.overflow = '';
    }
    if (closeSidebar) {
        closeSidebar.addEventListener('click', closeSidebarFunction);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebarFunction);
    }
    // -------------------------------------------------------------------
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (!link.classList.contains('logout-btn')) {
                closeSidebarFunction();
            }
        });
    });

    if (sidebarThemeSwitcher) {
        sidebarThemeSwitcher.addEventListener('click', toggleTheme);
    }

    if (sidebarLanguageSwitcher) {
        sidebarLanguageSwitcher.addEventListener('click', toggleLanguage);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileSidebar.classList.contains('open')) {
            closeSidebarFunction();
        }
    });
}

//عشان الجلوبال اكسيس
window.logout = logout;
window.toggleEditMode = toggleEditMode;
window.saveProfile = saveProfile;
window.cancelEdit = cancelEdit;

// Course Detail Page Functionality
function initializeCourseDetailPage() {
    const videoPlayer = document.getElementById('videoPlayer');
    const currentLectureTitle = document.getElementById('currentLectureTitle');
    const currentLectureDescription = document.getElementById('currentLectureDescription');
    const toggleSidebar = document.getElementById('toggleSidebar');
    const lecturesSidebar = document.querySelector('.lectures-sidebar');
    const videoQuizBtn = document.getElementById('videoQuizBtn');

    // // Handle lecture item clicks
    lectureItems.forEach(item => {
        item.addEventListener('click', function() {
            lectureItems.forEach(lecture => lecture.classList.remove('active'));

            // Add active class to clicked item

            // const lectureId = this.getAttribute('data-lecture-id');
            // const lectureTitle = this.querySelector('.lecture-title').textContent;
            // const lectureDescription = this.querySelector('.lecture-description').textContent;

            // const videoElement = videoPlayer.querySelector('.video-element');
            // videoElement.src = `https://example.com/video${lectureId}.mp4`;

            // currentLectureTitle.textContent = lectureTitle;
            // currentLectureDescription.textContent = lectureDescription;

            // if (videoQuizBtn) {
            //     videoQuizBtn.setAttribute('data-lecture-id', lectureId);
            // }

            if (window.innerWidth <= 992) {
                videoPlayer.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    if (toggleSidebar) {
        toggleSidebar.addEventListener('click', function() {
            lecturesSidebar.classList.toggle('collapsed');
        });
    }

    // if (videoQuizBtn) {
    //     videoQuizBtn.addEventListener('click', function() {
    //         const lectureId = this.getAttribute('data-lecture-id');
    //         const lectureTitle = currentLectureTitle.textContent;

    //         showQuizModal();
    //     });
    // }
}

// Quiz Modal Function
function showQuizModal() {
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'quiz-modal-overlay';
    modalOverlay.innerHTML = `
        <div class="quiz-modal">
            <div class="quiz-modal-header">
                <h3>📝 Quiz: one</h3>
                <button class="close-quiz-modal">×</button>
            </div>
            <div class="quiz-modal-content">
                <div class="quiz-info">
                    <p><strong>Lecture:</strong> q</p>
                    <p><strong>Questions:</strong> 10 Multiple Choice</p>
                    <p><strong>Time Limit:</strong> 15 minutes</p>
                    <p><strong>Passing Score:</strong> 70%</p>
                </div>
                <div class="quiz-actions">
                    <button class="start-quiz-btn"">
                        <span class="quiz-icon">🚀</span>
                        Start Quiz
                    </button>
                    <button class="cancel-quiz-btn">
                        <span class="quiz-icon">❌</span>
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    `;


    document.body.appendChild(modalOverlay);

    const modalStyles = document.createElement('style');
    modalStyles.textContent = `
        .quiz-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        }

        .quiz-modal {
            background: linear-gradient(135deg, #f5deb3, #f4e4c1);
            border-radius: 20px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 2px solid rgba(212, 175, 55, 0.3);
            position: relative;
        }

        body.dark-mode .quiz-modal {
            background: linear-gradient(135deg, #243a6b, #1a2a4a);
            border-color: rgba(212, 175, 55, 0.5);
        }

        .quiz-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(212, 175, 55, 0.3);
        }

        .quiz-modal-header h3 {
            font-family: 'Cinzel Decorative', serif;
            font-size: 1.5rem;
            color: #243a6b;
            margin: 0;
        }

        body.dark-mode .quiz-modal-header h3 {
            color: #f5deb3;
        }

        .close-quiz-modal {
            background: none;
            border: none;
            font-size: 2rem;
            color: #666;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .close-quiz-modal:hover {
            background: rgba(212, 175, 55, 0.2);
            color: #243a6b;
            transform: scale(1.1);
        }

        body.dark-mode .close-quiz-modal {
            color: #b8c5d6;
        }

        body.dark-mode .close-quiz-modal:hover {
            background: rgba(212, 175, 55, 0.2);
            color: #f5deb3;
        }

        .quiz-info {
            margin-bottom: 2rem;
        }

        .quiz-info p {
            margin-bottom: 0.8rem;
            color: #333;
            font-size: 1rem;
        }

        body.dark-mode .quiz-info p {
            color: #e7eef8;
        }

        .quiz-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }

        .start-quiz-btn, .cancel-quiz-btn {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .start-quiz-btn {
            background: linear-gradient(135deg, #243a6b, #1a2a4a);
            color: #f5deb3;
        }

        .start-quiz-btn:hover {
            background: linear-gradient(135deg, #d4af37, #f5deb3);
            color: #243a6b;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
        }

        .cancel-quiz-btn {
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
        }

        .cancel-quiz-btn:hover {
            background: linear-gradient(135deg, #c82333, #a71e2a);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
        }

        body.dark-mode .start-quiz-btn {
            background: linear-gradient(135deg, #d4af37, #f5deb3);
            color: #243a6b;
        }

        body.dark-mode .start-quiz-btn:hover {
            background: linear-gradient(135deg, #243a6b, #1a2a4a);
            color: #f5deb3;
        }

        @media (max-width: 768px) {
            .quiz-modal {
                margin: 1rem;
                padding: 1.5rem;
            }

            .quiz-actions {
                flex-direction: column;
            }

            .start-quiz-btn, .cancel-quiz-btn {
                width: 100%;
                justify-content: center;
            }
        }
    `;
    document.head.appendChild(modalStyles);

    const closeBtn = modalOverlay.querySelector('.close-quiz-modal');
    const cancelBtn = modalOverlay.querySelector('.cancel-quiz-btn');
    const startBtn = modalOverlay.querySelector('.start-quiz-btn');

    const closeModal = () => {
        document.body.removeChild(modalOverlay);
        document.head.removeChild(modalStyles);
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });

    startBtn.addEventListener('click', () => {
        closeModal();
        alert(`Starting quiz for Lecture ${lectureId}: ${lectureTitle}`);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

if (document.querySelector('.course-detail-page')) {
    initializeCourseDetailPage();
}

    // function initializeContactForm() {
    //     const contactForm = document.getElementById('contactForm');
    //
    //     if (contactForm) {
    //         contactForm.addEventListener('submit', function(e) {
    //             e.preventDefault();
    //
    //             const formData = new FormData(this);
    //
    //             const submitBtn = this.querySelector('.submit-btn');
    //             const originalText = submitBtn.innerHTML;
    //
    //             submitBtn.innerHTML = '<span class="btn-icon">⏳</span>Sending...';
    //             submitBtn.disabled = true;
    //
    //             setTimeout(() => {
    //                 showNotification('Message sent successfully! We\'ll get back to you within 24 hours.', 'success');
    //                 this.reset();
    //                 submitBtn.innerHTML = originalText;
    //                 submitBtn.disabled = false;
    //             }, 2000);
    //         });
    //         contactForm.submit();
    //     }
    // }

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showNotification(message, type = 'info') {
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close">×</button>
        </div>
    `;

    // Add styles
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(212, 175, 55, 0.2);
        }

        .notification-success {
            background: rgba(40, 167, 69, 0.9);
            color: white;
        }

        .notification-error {
            background: rgba(220, 53, 69, 0.9);
            color: white;
        }

        .notification-info {
            background: rgba(23, 162, 184, 0.9);
            color: white;
        }

        .notification-icon {
            font-size: 1.2rem;
        }

        .notification-message {
            flex: 1;
            font-weight: 500;
        }

        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.3s ease;
        }

        .notification-close:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        body.dark-mode .notification-content {
            background: rgba(26, 26, 26, 0.9);
            border-color: rgba(212, 175, 55, 0.3);
        }
    `;

    document.head.appendChild(notificationStyles);
    document.body.appendChild(notification);

    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            if (notificationStyles.parentNode) {
                notificationStyles.parentNode.removeChild(notificationStyles);
            }
        }, 300);
    });

    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                if (notificationStyles.parentNode) {
                    notificationStyles.parentNode.removeChild(notificationStyles);
                }
            }, 300);
        }
    }, 5000);
}

if (document.querySelector('.contact-page')) {
    initializeContactForm();
}


// Logout function for navbar
function logout() {
    localStorage.removeItem('thuthGateUser');
    window.location.href = 'index.html';
}
document.addEventListener("DOMContentLoaded", () => {
    const timerElement = document.getElementById("timer");

    // Parse end time from data attribute and convert to milliseconds
    const endTime = new Date(timerElement.getAttribute("data-end")).getTime();

    let timerInterval;
    // Function to update the timer
    function updateTimer() {
        const now = new Date().getTime();
        let diff = Math.floor((endTime - now) / 1000.0);
        if (diff <= 0) {
            timerElement.textContent = "00:00";
            clearInterval(timerInterval);
            alert("⏰ Time's up!");
            document.querySelector(".quiz-form").submit();
            return;
        }

        const minutes = Math.floor(diff / 60);
        const seconds = diff % 60;

        timerElement.textContent =
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    // Initial call to display timer immediately
    updateTimer();

    // Declare and initialize interval
    timerInterval = setInterval(updateTimer, 1000);
});
function normalizeText(text) {
    return text.replace(/\s+/g, " ").trim(); // collapse spaces & line breaks
}

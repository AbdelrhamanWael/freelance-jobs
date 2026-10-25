@php use Illuminate\Support\Facades\Auth; @endphp
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Th𝕆th Gate - Grade Chat</title>
    <meta name="user-id" content="{{ Auth::id() }}">
    <meta name="student-id" content="{{ auth()->user()->student->id }}">
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">
    <link rel="stylesheet" href="/styles.css">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    @vite(['resources/js/app.js'])
</head>

<body class="chat-page" style="display: flex; flex-direction: column;  height: 100vh;">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <header class="main-header" style="flex-shrink: 0;">
        <div class="header-content">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <button class="hamburger-menu" id="hamburgerMenu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <nav class="main-nav">
                <ul>
                    <li><a href="/student/home">Home</a></li>
                    <li><a href="/courses">Courses</a></li>
                    <li><a href="/community" class="active">Chat</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/profile">Profile</a></li>
                    <li>
                        <form method="POST" action="/logout" id="logoutForm">
                            @csrf
                            @method('DELETE')
                            <a href="#" class="logout-btn"
                                onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                        </form>
                    </li>
                </ul>
            </nav>
            <div class="switchers-container">
                <button class="theme-switcher" id="themeSwitcher" title="Toggle Dark Mode">
                    <span class="theme-icon">🌙</span>
                </button>
                <button class="language-switcher" id="languageSwitcher" title="Switch Language">
                    <span class="language-text">EN</span>
                </button>
            </div>
            <span class="student-points" title="Your Points">
                Points: <span id="studentPointsValue">{{ Auth::user()->student->points }}</span>
            </span>
        </div>
    </header>
    <div class="mobile-sidebar" id="mobileSidebar">
        <div class="sidebar-header">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <button class="close-sidebar" id="closeSidebar">
                <span></span>
                <span></span>
            </button>
        </div>
        <nav class="sidebar-nav">
            <ul>
                <li><a href="/student/home">Home</a></li>
                <li><a href="/courses">Courses</a></li>
                <li><a href="/community" class="active">Chat</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/profile">Profile</a></li>
                <li>
                    <form method="POST" action="/logout" id="logoutForm">
                        @csrf
                        @method('DELETE')
                        <a href="#" class="logout-btn"
                            onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                    </form>
                </li>
            </ul>
            <span class="student-points-side" title="Your Points"
                style="  justify-self: center;margin: 50px auto;display: block;">
                Points: <span id="studentPointsValueSide">{{ Auth::user()->student->points }}</span>
            </span>
        </nav>
        <div class="sidebar-switchers">
            <button class="theme-switcher" id="sidebarThemeSwitcher" title="Toggle Dark Mode">
                <span class="theme-icon">🌙</span>
            </button>
            <button class="language-switcher" id="sidebarLanguageSwitcher" title="Switch Language">
                <span class="language-text">EN</span>
            </button>
        </div>
    </div>
    <section class="chat-column" style="flex: 1;  display: flex;  flex-direction: column;">
        <div id="scrollToBottomBtn" class="scroll-to-bottom-btn" title="Scroll to latest message" style="display:none;"
            onclick="scrollToLatestMessage()">
            <span class="scroll-arrow">⬇</span>
        </div>
        <div class="chat-messages" id="chatMessages">
            @foreach ($messages as $message)
                <div class="message {{ $message->user_id === Auth::id() ? 'user-message' : 'other-message' }} {{ $message->deleted ? 'deleted-message' : '' }}"
                    data-id="{{ $message->id }}" data-user-id="{{ $message->user_id }}">

                    <div class="message-avatar">
                        @unless ($message->deleted)
                            @if ($message->user->type === 1)
                                <img src="/imgs/teacher.png" alt="Teacher">
                            @else
                                <img src="/imgs/profile.png" alt="Student">
                            @endif
                        @endunless
                    </div>

                    <div class="message-content">
                        <div class="message-header">
                            <span
                                class="message-author">{{ ($message->user->type == 1 ? 'Mr.' : '') . $message->user->name }}</span>
                            <span class="message-time">{{ $message->time }}</span>
                        </div>

                        @if ($message->reply_to && $message->replyMessage)
                            <div class="reply-box">
                                <strong>{{ $message->replyMessage->user->name }}</strong><br>
                                @if ($message->replyMessage->deleted)
                                    <span>This message was deleted.</span>
                                @else
                                    @if ($message->replyMessage->message)
                                        <span>{{ $message->replyMessage->message }}</span>
                                    @endif
                                    @if ($message->replyMessage->image)
                                        <img src="{{ asset($message->replyMessage->image) }}" alt="Reply Image"
                                            style="max-width: 80px; max-height: 80px; border-radius: 6px; margin-top: 4px;">
                                    @endif
                                @endif
                            </div>
                        @endif


                        @if ($message->deleted)
                            <span>{{ $message->message }}</span>
                        @else
                            @if ($message->message)
                                <p>{{ $message->message }}</p>
                            @endif
                            @if ($message->image)
                                <img src="{{ asset($message->image) }}" alt="Community Image"
                                    style="max-width: 100%; height: auto; margin-top: 8px;">
                            @endif
                        @endif
                    </div>
                </div>
            @endforeach
        </div>

        <div class="chat-input-container sticky-composer" style="margin-top: 16px;">
            <div id="replyPreview" class="reply-preview" style="display:none;">
                <span id="replyAuthor"></span>: <span id="replyText"></span>
                <button type="button" onclick="cancelReply()">✖</button>
            </div>
            <div id="imagePreview" class="preview-container"
                style="margin: 10px; display:flex; gap:10px; flex-wrap:wrap;"></div>
            <form id="chatForm" enctype="multipart/form-data">
                <div class="input-group">
                    <input type="hidden" name="community_id" value="{{ $fullCommunity->id }}">
                    <input type="hidden" name="reply_to" id="replyToInput">

                    <input type="text" name="message" id="messageInput" placeholder="Type your message."
                        maxlength="500" autocomplete="off">
                    <button type="submit" class="send-btn"><span class="send-icon"
                            id = "send-span">📤</span></button>
                    <input type="file" id="imageIn" name="image" accept="image/*" style="display: none;">
                    <button type = "button" onclick="document.getElementById('imageIn').click()"
                        class="image-btn"><span>🔗</span></button>
                </div>
            </form>
        </div>
    </section>
    <div id="deleteMsgModal" class="delete-modal" style="display:none;">
        <div class="delete-modal-content">
            <p>Are you sure you want to delete this message?</p>
            <div class="delete-modal-actions">
                <button id="deleteMsgYes" class="btn btn-delete">Delete</button>
                <button id="replyMsgBtn" class="btn">Reply</button>
                <button id="deleteMsgNo" class="btn">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        const modal = document.getElementById('deleteMsgModal');
        const replyBtn = document.getElementById('replyMsgBtn');

        replyBtn.onclick = function() {
            if (msgToDelete) {
                setReply(msgToDelete);
            }
            modal.style.display = "none";
            msgToDelete = null;
        };
    </script>

    <script>
        const imageInput = document.getElementById('imageIn');
        const imagePreview = document.getElementById('imagePreview');

        imageInput.addEventListener('change', () => {
            imagePreview.innerHTML = "";

            const files = imageInput.files;
            if (!files.length) return;

            Array.from(files).forEach(file => {
                if (!file.type.startsWith("image/")) return;

                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.style.maxWidth = "200px";
                    img.style.maxHeight = "150px";
                    img.style.borderRadius = "8px";
                    img.style.objectFit = "cover";
                    imagePreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    </script>



    <script>
        window.addEventListener('DOMContentLoaded', () => {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });

        const chatForm = document.getElementById('chatForm');
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        let icon = document.getElementById('send-span');
        let sendbtn = document.querySelector('.send-btn');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(chatForm);
            const message = messageInput.value.trim();
            const image = document.getElementById('imageIn').files[0];

            if (!message && !image) return;

            icon.textContent = '⏳';
            sendbtn.disabled = true;
            messageInput.value = '';
            imagePreview.innerHTML = '';
            document.getElementById('imageIn').value = '';

            try {
                await fetch('/community', {
                    method: 'POST',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
                    },
                    body: formData
                });

            } catch (err) {
                alert('message faild to send');
                console.error(err);
            }

            cancelReply();

            chatMessages.scrollTop = chatMessages.scrollHeight;
            icon.textContent = '📤';
            sendbtn.disabled = false;
        });


        window.addEventListener('DOMContentLoaded', () => {
            const chatMessages = document.getElementById('chatMessages');

            chatMessages.scrollTop = chatMessages.scrollHeight;


            window.Echo.channel('MessageChannel')
                .listen('.App\\Events\\MessageEvent', (e) => {
                    const msg = e.message;
                    const div = document.createElement('div');

                    div.setAttribute("data-id", msg.id);
                    div.setAttribute("data-user-id", msg.user.id);

                    const isNearBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages
                        .scrollHeight - 50;

                    div.className = msg.user.id === parseInt(document.querySelector('meta[name="user-id"]')
                            ?.content) ?
                        'message user-message' :
                        'message other-message';

                    div.innerHTML = `
    <div class="message-avatar">
        <img src="${msg.user.type === 1 ? '/imgs/teacher.png' : '/imgs/profile.png'}" alt="User">
    </div>
    <div class="message-content">
        <div class="message-header">
            <span class="message-author">${msg.user.type === 1 ? 'Mr.' : ''}${msg.user.name}</span>
            <span class="message-time">${msg.time}</span>
        </div>
        
        ${msg.reply_to && msg.replyMessage ? `
                                                <div class="reply-box">
                                                    <strong>${msg.replyMessage.user.name}</strong><br>
                                                    ${
                                                        msg.replyMessage.deleted
                                                            ? '<span>This message was deleted.</span>'
                                                            : `
                            ${msg.replyMessage.message ? `<span>${msg.replyMessage.message.substring(0, 50)}</span>` : ''}
                            ${msg.replyMessage.image ? `<img src="/${msg.replyMessage.image}" alt="Reply Image"
                                                                    style="max-width:80px; max-height:80px; border-radius:6px; margin-top:4px;">` : ''}
                        `
                                                    }
                                                </div>
                                            ` : ''}
        
        ${msg.message ? `<p>${msg.message}</p>` : ''}
        ${msg.image ? `<img src="/${msg.image}" alt="Image" style="max-width:100%; margin-top:8px;">` : ''}
    </div>
`;

                    chatMessages.appendChild(div);

                    // handle scrolling
                    const scrollToBottom = () => {
                        if (isNearBottom) {
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }
                    };

                    const img = div.querySelector("img[alt='Image']");
                    if (img) {
                        img.addEventListener("load", scrollToBottom);
                        img.addEventListener("error", scrollToBottom);
                    } else {
                        scrollToBottom();
                    }
                });
        });
    </script>

    <script>
        function setReply(msg) {
            let id = msg.dataset.id;
            let author = msg.querySelector(".message-author")?.textContent || "Unknown";
            let text = msg.querySelector("p")?.textContent || "[Image]";

            document.getElementById("replyToInput").value = id;
            document.getElementById("replyAuthor").textContent = author;
            document.getElementById("replyText").textContent = text;
            document.getElementById("replyPreview").style.display = "block";
        }

        function cancelReply() {
            document.getElementById("replyToInput").value = "";
            document.getElementById("replyPreview").style.display = "none";
        }


        let msgToDelete = null;
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chatMessages');
            const modal = document.getElementById('deleteMsgModal');
            const yesBtn = document.getElementById('deleteMsgYes');
            const noBtn = document.getElementById('deleteMsgNo');
            let longPressTimer = null;

            chatMessages.addEventListener('contextmenu', function(e) {
                let msg = e.target.closest('.message');
                if (!msg || msg.classList.contains('deleted-message')) return;

                const currentUserId = document.querySelector('meta[name="user-id"]')?.content;
                e.preventDefault();

                if (msg.getAttribute("data-user-id") === currentUserId) {
                    msgToDelete = msg;
                    modal.style.display = 'flex';
                } else {
                    setReply(msg);
                }
            });


            // Mobile:
            chatMessages.addEventListener('touchstart', function(e) {
                let msg = e.target.closest('.message');
                const currentUserId = document.querySelector('meta[name="user-id"]')?.content;

                if (msg &&
                    !msg.classList.contains('deleted-message') &&
                    msg.getAttribute("data-user-id") === currentUserId) {

                    longPressTimer = setTimeout(function() {
                        msgToDelete = msg;
                        modal.style.display = 'flex';
                    }, 600);
                } else {
                    setReply(msg);
                }
            });
            chatMessages.addEventListener('touchend', function(e) {
                clearTimeout(longPressTimer);
            });
            chatMessages.addEventListener('touchmove', function(e) {
                clearTimeout(longPressTimer);
            });

            yesBtn.onclick = async function() {
                if (msgToDelete) {
                    const msgId = msgToDelete.getAttribute("data-id");

                    try {
                        const res = await fetch(`/community/message/${msgId}`, {
                            method: "DELETE",
                            headers: {
                                "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
                                    .content,
                            },
                        });

                        if (res.ok) {
                            msgToDelete.classList.add("deleted-message");
                            const content = msgToDelete.querySelector(".message-content");

                            if (content) {
                                const header = content.querySelector(".message-header");
                                const author = header?.querySelector(".message-author")?.outerHTML || "";
                                const time = header?.querySelector(".message-time")?.outerHTML || "";

                                content.innerHTML = `
                                    <div class="message-header">
                                        ${author}
                                        ${time}
                                    </div>
                                    <span>This message was deleted.</span>
                                `;
                            }

                            const avatar = msgToDelete.querySelector(".message-avatar");
                            if (avatar) avatar.innerHTML = "";
                        } else {
                            alert("Could not delete message.");
                        }
                    } catch (err) {
                        console.error("Error deleting message:", err);
                    }
                }
                modal.style.display = "none";
                msgToDelete = null;
            };

            noBtn.onclick = function() {
                modal.style.display = 'none';
                msgToDelete = null;
            };

            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.style.display = 'none';
                    msgToDelete = null;
                }
            });

            window.Echo.channel('MessageChannel')
                .listen('.MessageDeletedEvent', (e) => {
                    const msgId = e.message_id;
                    const msgEl = document.querySelector(`.message[data-id="${msgId}"]`);

                    if (msgEl) {
                        msgEl.classList.add("deleted-message");

                        const content = msgEl.querySelector(".message-content");
                        if (content) {
                            const header = content.querySelector(".message-header");
                            const author = header?.querySelector(".message-author")?.outerHTML || "";
                            const time = header?.querySelector(".message-time")?.outerHTML || "";

                            content.innerHTML = `
                    <div class="message-header">
                        ${author}
                        ${time}
                    </div>
                    <span>${e.message}</span>
                `;
                        }

                        const avatar = msgEl.querySelector(".message-avatar");
                        if (avatar) avatar.innerHTML = "";
                    }
                });

        });

        const scrollBtn = document.getElementById('scrollToBottomBtn');

        function checkScrollBtn() {
            if (!chatMessages || !scrollBtn) return;
            const atBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 10;
            scrollBtn.style.display = atBottom ? 'none' : 'flex';
        }

        function scrollToLatestMessage() {
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        if (chatMessages && scrollBtn) {
            chatMessages.addEventListener('scroll', checkScrollBtn);
            setTimeout(checkScrollBtn, 500);
        }
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};

            window.Echo.private(`student.notification.${studentId}`)
                .listen('.student.notification', (e) => {
                    let toast = document.getElementById("toast");
                    toast.textContent = `📢 ${e.message}`;
                    toast.classList.add("show");

                    setTimeout(() => {
                        toast.classList.remove("show");
                    }, 3000);
                });
        });
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const studentId = {{ auth()->user()->student->id }};
            const pointsValueElement = document.getElementById("studentPointsValue");
            const pointsValueElementSide = document.getElementById("studentPointsValueSide");

            window.Echo.private(`AddPoints.${studentId}`)
                .listen('.points.added', (e) => {
                    if (pointsValueElement) {
                        let currentPoints = parseInt(pointsValueElement.textContent) || 0;
                        pointsValueElement.textContent = currentPoints + parseInt(e.points);
                    }

                    if (pointsValueElementSide) {
                        let currentPointsSide = parseInt(pointsValueElementSide.textContent) || 0;
                        pointsValueElementSide.textContent = currentPointsSide + parseInt(e.points);
                    }
                });
        });
    </script>
    <div id="toast" class="toast"></div>

    <script src="/script.js"></script>
</body>

</html>

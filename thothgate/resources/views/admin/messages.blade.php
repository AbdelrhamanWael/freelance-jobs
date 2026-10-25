<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Messages</title>
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon">

    <link rel="stylesheet" href="/styles.css">
    <link rel="stylesheet" href="/admin-styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>

<body class="admin-messages-page">
    <div id="loader">
        <!-- You can add an image, a CSS spinner, or text here -->
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <header class="main-header">
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
                    <li><a href="/admin/home">Dashboard</a></li>
                    <li><a href="/admin/instructors">Instructors</a></li>
                    <li><a href="/admin/students">Students</a></li>
                    <li><a href="/admin/messages" class="active">Messages</a></li>
                    <li>
                        <a href="/admin/notifications" id="notifLink">
                            @if (App\Models\AdminNotification::where('is_read', false)->count() > 0)
                                <span class="notif-dot" id = "notif-dot">🔴</span>
                            @endif
                            Notifications
                        </a>
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

        </div>
    </header>
    <!-- Mobile Sidebar -->
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
                <li><a href="/admin/home">Home</a></li>
                <li><a href="/admin/instructors">Instructors</a></li>
                <li><a href="/admin/students">Students</a></li>
                <li><a href="/admin/messages" class="active">Messages</a></li>
                <li>
                    <a href="/admin/notifications" id="notifLink">
                        @if (App\Models\AdminNotification::where('is_read', false)->count() > 0)
                            <span class="notif-dot" id = "notif-dot">🔴</span>
                        @endif
                        Notifications
                    </a>
                </li>

            </ul>
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
    <div class="sidebar-overlay" id="sidebarOverlay"></div>


    <div class="admin-layout ">
        @if (session('success'))
            <div class="message success-general">
                {{ session('success') }}
            </div>
        @endif
        <main class="admin-main-content">

            <section class="admin-messages-section">
                <div class="container">
                    <div class="admin-messages-header contact-header">
                        <h1 class="section-title" style="margin: revert;">Student Messages</h1>
                        <p>View and manage messages sent by students.</p>
                    </div>
                    <div class="admin-messages-content contact-content-admin">
                        <div class="admin-messages-table-container contact-form-container">
                            <div class="messages-card-list">
                                @foreach ($messages as $message)
                                    <div class="message-card">
                                        <div class="message-card-header">
                                            <span class="message-id">{{ $message->id }}</span>
                                            <form action="/message/delete/{{ $message->id }}" method="POST">
                                                @csrf
                                                @method('DELETE')
                                                <button class="btn btn-delete" title="Delete">Delete</button>
                                            </form>
                                        </div>
                                        <div class="message-card-body">
                                            <h3 class="message-name">{{ $message->user->name }}</h3>
                                            <p class="message-email"><strong>Email:</strong> {{ $message->user->email }}
                                            </p>
                                            <p class="message-email"><strong>phone:</strong>
                                                {{ $message->user->phone_number }}
                                            </p>

                                            <p class="message-text"><strong>Subject: </strong>{{ $message->subject }}
                                            </p>

                                            <p class="message-text"><strong>Message: </strong>{{ $message->message }}
                                            </p>
                                            <p class="message-date"><strong>Date:</strong>
                                                {{ $message->created_at->format('d - m - Y') }}
                                            </p>
                                        </div>
                                    </div>
                                @endforeach
                            </div>

                            <div class="pagination" style="margin-top:2rem; justify-content: flex-end;">
                                {{ $messages->links('vendor.pagination.custom') }}
                            </div>
                        </div>
                    </div>

                </div>
            </section>
        </main>
    </div>


    <footer class="main-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Th𝕆th Gate Admin</h3>
                    <p>Gateway to Ancient Wisdom, Modern Learning</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/admin/home">Dashboard</a></li>
                        <li><a href="/admin/instructors">Instructors</a></li>
                        <li><a href="/admin/students">Students</a></li>
                        <li><a href="/admin/messages">Messages</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Contact</h4>
                    <p>Email: thothgate@gmail.com</p>
                    <p>Phone: +20 111 686 5363</p>
                </div>
                <div class="footer-section">
                    <h4>Follow Us</h4>
                    <div class="social-icons">
                        <a href="https://www.facebook.com/share/19ZWmoHhcz/" class="social-icon facebook"
                            target="_blank"> <i class="fab fa-facebook-f"></i></a>
                        <a href="https://www.instagram.com/gate61407?igsh=bWV3ejJlOGpzZmwy" target="_blank"
                            class="social-icon instagram"> <i class="fab fa-instagram"></i></a>
                        <a href="https://youtube.com/@tonyhany8314?si=W4N9yI_GT4gwW_xs" class="social-icon youtube"
                            target="_blank"><i class="fab fa-youtube"></i></a>
                        <a href="https://www.tiktok.com/@thothgate" class="social-icon tiktok" target="_blank"><i
                                class="fab fa-tiktok"></i></a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 Th𝕆th Gate Admin. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script>
        const message = document.querySelector(".message");

        if (message) {
            setTimeout(() => {
                message.classList.add("fade-out");
                message.addEventListener("animationend", () => {
                    message.remove();
                });
            }, 3000);
        }
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            window.Echo.channel('admin.notifications')
                .listen('AdminNotificationEvent', (e) => {
                    let toast = document.getElementById("toast");
                    toast.textContent = "📢 New Notification Received!";
                    toast.classList.add("show");

                    let notifLink = document.getElementById("notifLink");
                    if (!document.getElementById("notif-dot")) {
                        let dot = document.createElement("span");
                        dot.id = "notif-dot";
                        dot.className = "notif-dot";
                        dot.textContent = "🔴";
                        notifLink.insertBefore(dot, notifLink.childNodes[0]);
                    }

                    setTimeout(() => {
                        toast.classList.remove("show");
                    }, 2000);
                });

        });
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            window.Echo.channel('contact-messages')
                .listen('.new.contact.message', (e) => {
                    let messagesContainer = document.querySelector('.messages-card-list');

                    let card = document.createElement('div');
                    card.classList.add('message-card');
                    let date = new Date(e.message.created_at);
                    let formattedDate = `${date.getDate()} - ${date.getMonth()+1} - ${date.getFullYear()}`;

                    card.innerHTML = `
                    <div class="message-card-header">
                        <span class="message-id">${e.message.id}</span>
                        <form action="/message/delete/${e.message.id}" method="POST">
                            @csrf
                            @method('DELETE')
                            <button class="btn btn-delete" title="Delete">Delete</button>
                        </form>
                    </div>

                    <div class="message-card-body">
                        <h3 class="message-name">${e.user.name}</h3>
                        <p class="message-email"><strong>Email:</strong> ${e.user.email}</p>
                        <p class="message-email"><strong>Phone:</strong> ${e.user.phone_number || ''}</p>
                        <p class="message-text"><strong>Subject: </strong>${e.message.subject}</p>
                        <p class="message-text"><strong>Message: </strong>${e.message.message}</p>
                        <p class="message-date"><strong>Date:</strong> ${formattedDate}</p>
                    </div>
                `;
                    messagesContainer.prepend(card);
                });
        })
    </script>

    <div id="toast" class="toast"></div>

    <script src="/admin.js"></script>
    <script src="/script.js"></script>


</body>

</html>

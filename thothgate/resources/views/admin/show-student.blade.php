@php
    use App\Models\Course;
@endphp
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin - View Student</title>
    <link rel="icon" href="/imgs/logo.png" type="image/x-icon" />
    <link rel="stylesheet" href="/styles.css" />
    <link rel="stylesheet" href="/admin-styles.css" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&display=swap"
        rel="stylesheet" />
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>

<body class="view-student">
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
                    <li><a href="/admin/students" class="active">Students</a></li>
                    <li><a href="/admin/messages">Messages</a></li>
                    <li><a href="/admin/notifications" id="notifLink">
                            @if (App\Models\AdminNotification::where('is_read', false)->count() > 0)
                                <span class="notif-dot" id = "notif-dot">🔴</span>
                            @endif
                            Notifications
                        </a></li>

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
                <li><a href="/admin/messages">Messages</a></li>
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


    <div class="admin-layout">
        @if (session('success'))
            <div class="message success-general">
                {{ session('success') }}
            </div>
        @endif
        <main class="admin-main-content">
            <section class="admin-section" style="margin: auto;">
                <div class="admin-section-header">
                    <h2 class="section-title">View Student</h2>
                    <a href="/admin/students" class="btn">Back to Students</a>
                </div>
                <div class="widget" style="margin-bottom:2rem;">
                    <h3>Student Information</h3>
                    <ul class="student-info" style="list-style:none; padding:0;">
                        <li><strong>ID:</strong> {{ $student->id }}</li>
                        <li><strong>Name:</strong> {{ $student->user->name }}</li>
                        <li><strong>Email:</strong> {{ $student->user->email }}</li>
                        <li><strong>Current Grade:</strong> {{ $student->grade }}</li>
                        <li><strong>Quizes</strong><button class="btn"
                                onclick=" window.location.href = '/admin/exams/{{ $student->id }}';">View</button></li>
                    </ul>
                    <div style="display: contents;";>
                        <h3>Lectures Access:</h3>
                        <ul class="course-list">
                            @foreach ($purchasedLectures as $courseId => $lectures)
                                <li class="course">
                                    <strong>{{ Course::where('id', $courseId)->first()->subject }}</strong>
                                    <ul class="lectures">
                                        @foreach ($lectures as $lecture)
                                            <li>Lecture {{ $lecture->lecture->index }}</li>
                                        @endforeach
                                    </ul>
                                </li>
                            @endforeach
                        </ul>
                    </div>
                </div>
                <div class="widget-container">
                    <div class="widget">
                        <h3>Grant Access</h3>
                        <form id="grantAccessForm" method="POST" action="/open/lecture/{{ $student->id }}">
                            @csrf
                            <label for="courseSelect"><strong>Course:</strong></label>
                            <select id="courseSelect" class="search-bar" style="width:100%;margin-bottom:1rem;">
                                <option value="">-- Select Course --</option>
                                @foreach ($availableCourses as $av)
                                    <option value="{{ $av->id }}">{{ $av->subject }}</option>
                                @endforeach
                            </select>
                            <label for="lectureSelect"><strong>Lecture:</strong></label>
                            <select id="lectureSelect" name="lecture_id" class="search-bar"
                                style="width:100%;margin-bottom:1rem;">
                                <option value="">-- Select Lecture --</option>
                            </select>
                            <button type="submit" class="btn btn-edit" style="margin-top:1rem;">Grant
                                Access</button>
                        </form>
                    </div>
                    <div class="widget">
                        <h3>Remove Access</h3>
                        <form id="removeAccessForm" method="POST" action="/remove/lecture/{{ $student->id }}">
                            @csrf
                            @method('DELETE')
                            <label for="courseSelect2"><strong>Course:</strong></label>
                            <select id="courseSelect2" class="search-bar" style="width:100%;margin-bottom:1rem;">
                                <option value="">-- Select Course --</option>
                                @foreach ($availableCourses as $av)
                                    <option value="{{ $av->id }}">{{ $av->subject }}</option>
                                @endforeach
                            </select>
                            <label for="removeLectureSelect"><strong>Lecture:</strong></label>
                            <select id="removeLectureSelect" class="search-bar" name = "lecture_id"
                                style="width:100%;margin-bottom:1rem;">
                                <option value="">-- Select Lecture --</option>
                            </select>
                            <button class="btn btn-remove">Remove Access</button>
                        </form>
                    </div>
                    <div class="widget">
                        <h3>Grade Chat Access</h3>
                        <form id="gradeChatAccessForm" method="POST" action="/edit-end-date/{{ $student->id }}">
                            @csrf
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                <input type="checkbox" id="chatAccessCheckbox" name="chatAccessCheckbox" required>
                                <label for="chatAccessCheckbox" style="margin:0;">
                                    <strong>Enable chat access for current grade ({{ $student->grade }})</strong>
                                </label>
                            </div>
                            <div id="chatEndDateContainer" style="display:none;">
                                <label for="chatEndDate"><strong>End Date for Chat Access:</strong></label>
                                <input type="date" id="chatEndDate" name="chatEndDate"
                                    style="width:100%;margin-bottom:1rem;">
                            </div>

                            @error('chatEndDate')
                                <span class="message error">{{ $message }}</span>
                            @enderror
                            <button type="submit" class="btn btn-edit" style="margin-top:1rem;">Save</button>
                        </form>
                    </div>
                    <div class="widget">
                        <h3>Package Access</h3>
                        <form id="grantAccessForm" method="POST"
                            action="{{ route('grantPackage', [$student->id]) }}">
                            @csrf
                            <label for="courseSelect"><strong>Course:</strong></label>
                            <select name = "courseSelect" id="courseSelect" class="search-bar"
                                style="width:100%;margin-bottom:1rem;" required>
                                <option value="">-- Select Course --</option>
                                @foreach ($availableCourses as $av)
                                    <option value="{{ $av->id }}">{{ $av->subject }}</option>
                                @endforeach
                                <option value="all">All</option>
                            </select>
                            <button type="submit" class="btn btn-edit" style="margin-top:1rem;">Grant
                                Access</button>
                        </form>
                    </div>
                </div>

                <div id="accessMessage" style="margin-top:1rem;"></div>
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
                <p>© 2025 Th𝕆th Gate Admin. All rights reserved.</p>
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
        window.availableLectures = @json($availableLectures);

        document.getElementById('courseSelect').addEventListener('change', function() {
            const selectedCourseId = this.value;
            const lectureSelect = document.getElementById('lectureSelect');

            lectureSelect.innerHTML = '<option value="">-- Select Lecture --</option>';

            if (selectedCourseId) {
                const filteredLectures = window.availableLectures.filter(lecture => lecture.course_id ==
                    selectedCourseId);

                filteredLectures.forEach(lecture => {
                    const option = document.createElement('option');
                    option.value = lecture.id;
                    option.textContent = `Lecture ${lecture.index}`;
                    lectureSelect.appendChild(option);
                });
            }
        });

        window.purchased = @json($purchased);
        document.getElementById('courseSelect2').addEventListener('change', function() {
            const course_id = this.value;
            const lectures = document.getElementById('removeLectureSelect');
            lectures.innerHTML = '<option value="">-- Select Lecture --</option>';

            if (course_id) {
                const filterLecs = window.purchased.filter(lecture => lecture.course_id == course_id);
                filterLecs.forEach(lecture => {
                    const option = document.createElement('option');
                    option.value = lecture.id;
                    option.textContent = `Lecture ${lecture.index}`;
                    lectures.appendChild(option);
                });
            }
        });
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
        document.querySelectorAll(".course > strong").forEach(course => {
            course.addEventListener("click", () => {
                course.parentElement.classList.toggle("open");
            });
        });

        document.getElementById('chatAccessCheckbox').addEventListener('change', function() {
            document.getElementById('chatEndDateContainer').style.display = this.checked ? 'block' : 'none';
        });
    </script>
    <script src="/admin.js"></script>
    <script src="/script.js"></script>
    <div id="toast" class="toast"></div>

</body>

</html>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Add Points</title>
    <link rel="stylesheet" href="/styles.css">
    <link rel="stylesheet" href="/instructor.css">
    <link rel="stylesheet" href="/instructor-students-styles.css">

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap"
        rel="stylesheet">
    @vite(['resources/js/app.js'])

</head>

<body class="instructor-home">
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
                    <li><a href="/instructor/home">Home</a></li>
                    <li><a href="/instructor/create/exam">Create Exam</a></li>
                    <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                    <li><a href="/instructor/chats">Chats</a></li>
                    <li><a href="/instructor/students">Students</a></li>
                    <li>
                        <form method="POST" action="/logout" id = "logoutForm">
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
                <li><a href="/instructor/home">Home</a></li>
                <li><a href="/instructor/create/exam">Create Exam</a></li>
                <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                <li><a href="/instructor/chats">Chats</a></li>
                <li><a href="/instructor/students">Students</a></li>
                <li>
                    <form method="POST" action="/logout" id = "logoutForm">
                        @csrf
                        @method('DELETE')
                        <a href="#" class="logout-btn"
                            onclick="document.getElementById('logoutForm').submit(); return false;">Logout</a>
                    </form>
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

    <main class="container">
        <h1 class="section-title" style="margin: revert;">Add Points to Student</h1>
        <p style="text-align:center; margin-bottom: 2rem;">Award points to a student for their achievements</p>

        <!-- Student Info Card -->
        <div class="student-info-card" id="studentInfoCard">
            <div style="text-align: center;">
                <img id="studentAvatar" src="/imgs/profile.png" alt="Student Avatar"
                    style="width: 100px; height: 100px; border-radius: 50%; margin-bottom: 1rem; object-fit: cover; border: 4px solid #d4af37;">
                <h2 style=" margin-bottom: 0.5rem;">{{ $student->user->name }}</h2>
                <p style=" margin-bottom: 0.5rem;">ID: {{ $student->id }}</p>
                <p style=" margin-bottom: 0.5rem;">{{ $student->grade }}</p>
                <div
                    style="background: linear-gradient(135deg, #d4af37, #f5deb3); color: #243a6b; padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; font-weight: 600;">
                    Current Points: {{ $student->points }}
                </div>
            </div>
        </div>

        <div class="add-points-form">
            <form id="pointsForm" method="POST" action="{{ route('instructor.addPoints', $student->id) }}">
                @csrf
                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label for="pointsAmount" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Points
                        to
                        Add:</label>
                    <input type="number" id="pointsAmount" name="pointsAmount" required
                        style="width: 100%; padding: 12px 15px; border: 2px solid #d4af37; border-radius: 8px; font-size: 1rem; box-sizing: border-box;">
                </div>

                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label for="reason" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Reason for
                        Points:</label>
                    <select id="reason" name="reason" required
                        style="width: 100%; padding: 12px 15px; border: 2px solid #d4af37; border-radius: 8px; font-size: 1rem; box-sizing: border-box;">
                        <option value="">Select a reason...</option>
                        <option value="excellent_performance">Excellent Performance</option>
                        <option value="homework_completion">Homework Completion</option>
                        <option value="class_participation">Chat Participation</option>
                        <option value="behavior">Good Behavior</option>
                        <option value="exam_score">High Exam Score</option>
                    </select>
                </div>

                {{-- <div class="form-group" style="margin-bottom: 2rem;">
                    <label for="comments" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Additional
                        Comments (Optional):</label>
                    <textarea id="comments" name="comments" rows="4"
                        style="width: 100%; padding: 12px 15px; border: 2px solid #d4af37; border-radius: 8px; font-size: 1rem; box-sizing: border-box; resize: vertical;"
                        placeholder="Add any additional comments about this point award..."></textarea>
                </div> --}}

                <div class="form-actions" style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button type="submit" class="exam-btn" style="padding: 12px 30px; font-size: 1.1rem;">Add
                        Points</button>
                    <a href="instructor-students.html" class="exam-btn" style="text-align:center">Cancel</a>
                </div>
            </form>
        </div>


        <div id="successMessage"
            style="display: none; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem; box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);">
            <h3 style="margin-bottom: 0.5rem;"><i class="fas fa-check-circle"></i> Points Added Successfully!</h3>
            <p id="successText">The points have been added to the student's account.</p>
            <button onclick="window.location.href='{{ route('instructor.students') }}'" class="exam-btn"
                style="margin-top: 1rem; background: white; color: #4CAF50;">Back to Students</button>
        </div>
    </main>

    <footer class="main-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Th𝕆th Gate</h3>
                    <p>Gateway to Ancient Wisdom, Modern Learning</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/instructor/home">Home</a></li>
                        <li><a href="/instructor/create/exam">Create Exam</a></li>
                        <li><a href="/instructor/add/lecture">Add Lecture</a></li>
                        <li><a href="/instructor/chats">Chats</a></li>
                        <li><a href="/instructor/students">Students</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Contact</h4>
                    <a href="mailto:thothgate@gmail.com" 
                    style="color: #FFFFFF; text-decoration: none;">
                    thothgate@gmail.com
                    </a>
                    <p>Phone: +20 111 686 5363</p>
                    <p>WA Business: +20 100 934 1350</p>
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
                <p>&copy; 2025 Th𝕆th Gate Learning Center. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/script.js"></script>
    <script src="/instructor.js"></script>
    <script>
        document.getElementById('pointsForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const pointsAmount = parseInt(document.getElementById('pointsAmount').value);
            const reason = document.getElementById('reason').value;

            if (!pointsAmount || pointsAmount < 1) {
                alert('Please enter a valid number of points (minimum 1).');
                return;
            }
            if (!reason) {
                alert('Please select a reason for awarding points.');
                return;
            }

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({
                        pointsAmount,
                        reason,
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    document.body.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });

                    document.querySelector('.add-points-form').style.display = 'none';
                    document.getElementById('studentInfoCard').style.display = 'none';

                    const successText = document.getElementById('successText');
                    successText.innerHTML = `
                <strong>${pointsAmount} points</strong> have been added for <strong>${reason.replace('_', ' ')}</strong>.
            `;


                    document.getElementById('successMessage').style.display = 'block';


                } else {
                    alert("Something went wrong!");
                }

            } catch (error) {
                console.error(error);
                alert("Failed to save points. Please try again.");
            }
        });


        function goBack() {
            window.location.href = 'instructor-students.html';
        }
    </script>
</body>

</html>

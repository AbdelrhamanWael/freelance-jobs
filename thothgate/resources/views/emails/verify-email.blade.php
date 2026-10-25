<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Email - Thuth Gate</title>
    <link rel="stylesheet" href="/styles.css">
    <link
        href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;500;600;700&display=swap"
        rel="stylesheet">
</head>

<body class="login-page">
    <div class="login-container">
        <div class="login-header">
            <div class="logo-container">
                <img src="/imgs/logo.png" alt="Th𝕆th Gate Logo" class="logo-image">
                <h1 class="site-logo">Th𝕆th Gate</h1>
            </div>
            <p class="tagline">Gateway to Ancient Wisdom, Modern Learning</p>
        </div>
        <div class="login-form-container">
            <h2 class="section-title">Verify Your Email</h2>
            <div class="form-group" style="text-align:center;">
                <p style="font-size:1.2rem;color:#243a6b;margin-bottom:1.5rem;">Hello {{ $notifiable->name }},</p>
                <p style="font-size:1.1rem;color:#243a6b;margin-bottom:1.5rem;">Please click the button below to verify
                    your email address and access Th𝕆th Gate:</p>
                <a href="{{ $url }}" class="login-btn" style="margin-bottom:1rem;">Verify Email</a>
                <p style="margin-top:1rem;color:#d4af37;">If you didn’t create an account, you can safely ignore this
                    email.</p>
            </div>
        </div>
    </div>
    <div class="hieroglyph-bg"></div>
</body>

</html>

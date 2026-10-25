<?php

use App\Http\Middleware\CheckExamSession;
use App\Http\Middleware\EnsureUserIsStudent;
use App\Http\Middleware\PreventMultipleLogins;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use App\Http\Middleware\CheckAdmin;
use App\Http\Middleware\EnsureInstructor;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        channels: __DIR__.'/../routes/channels.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias([
            'check.exam' => CheckExamSession::class,
            'student' => EnsureUserIsStudent::class,
            'prevent.multiple.logins' => PreventMultipleLogins::class,
            'check.admin' => CheckAdmin::class,
            'check.instructor' => EnsureInstructor::class,
         ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();

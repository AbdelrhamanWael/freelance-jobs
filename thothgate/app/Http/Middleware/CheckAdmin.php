<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;

class CheckAdmin
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (Auth::check()) {
            if (Auth::user()->type == 1) {
                return redirect()->route('instructors.home')->with('error', 'You are not allowed to view this page');
            } else if (Auth::user()->type == 0) {
                return redirect()->route('home')->with('error', 'You are not allowed to view this page');
            }
        } else {
            return redirect()->route('login');
        }
        return $next($request);
    }
}

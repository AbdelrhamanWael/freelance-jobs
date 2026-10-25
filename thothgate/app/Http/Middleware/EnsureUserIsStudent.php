<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Illuminate\Support\Facades\Auth;
class EnsureUserIsStudent
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (Auth::check()) {
            if (Auth::user()->type == 2) {
                return redirect()->route('admin.home')->with('error', 'You are not allowed to view this page');
            } else if (Auth::user()->type == 1) {
                return redirect()->route('instructors.home')->with('error', 'You are not allowed to view this page');
            }
        } 
        else {
            return redirect()->route('login');
        }
        return $next($request);
    }
}

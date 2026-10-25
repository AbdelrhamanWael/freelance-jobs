<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;

class CheckExamSession
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $student = Auth::user()->student;

        if ($student) {
            $session = $student->sessions()
                ->whereNull('submitted_at')
                ->where('started_at', '<=', now())
                ->whereRaw("DATE_ADD(started_at, INTERVAL duration MINUTE) > NOW()")
                ->first();

            if ($session) {
                if (!$request->routeIs('exam.show')) {
                    return redirect()->route('exam.show', [
                        'course'  => $session->exam->lecture->course_id,
                        'lecture' => $session->exam->lecture_id,
                        'exam'    => $session->exam_id
                    ])->with('warning', 'You must finish your ongoing exam before doing anything else.');
                }
            }
        }
        return $next($request);
    }
}

<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\PurchasedLectures;
use App\Models\Student;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use App\Models\PointsHistroy;
use App\Models\StudentPackage;

class ProfileController extends Controller
{
    public function index()
    {
        $courses = Course::where('grade', Auth::user()->student->grade)->get();
        $finishedCounts = PurchasedLectures::select('course_id', DB::raw('count(*) as total'))
            ->where('student_id', Auth::user()->student->id)
            ->where('finished', 1)
            ->groupBy('course_id')
            ->pluck('total', 'course_id');
        $finished = [];
        foreach ($courses as $course) {
            $finished[] = [
                'subject' => $course->subject,
                'finished' => $finishedCounts[$course->id] ?? 0,
                'total' => $course->lectures->count(),
                'teacher' => $course->teacher,
            ];
        }

        $packages = StudentPackage::with('course')->where('student_id', Auth::user()->student->id)->get();
        // dd($packages);
        return view('profile', ['finished' => $finished , 'packages' => $packages]);
    }

    /**
     * @param Request $request
     * @param int $student_id
     * @return \Illuminate\Http\RedirectResponse
     */
    public function destroy(Request $request, $student_id)
    {
        $student = Student::findOrFail($student_id);

        /** @var \App\Models\User $user */
        $user = Auth::user();

        if (!$user->student || $user->student->id != $student_id) {
            return redirect()->route('home')->with('error', 'You don\'t have access to this page');
        }

        Auth::logout();
        $user->delete();

        return redirect()->route('welcome');
    }

    public function pointsHistory()
    {
        $student = Auth::user()->student;
        $pointsHistory = PointsHistroy::where('student_id', $student->id)->orderBy('created_at', 'desc')->get();
        return view('points-history', ['student' => $student, 'pointsHistory' => $pointsHistory]);
    }

    public function levels(){
        $student = Auth::user()->student;
        $level = Student::getLevel($student->points);
        return view('levels' , [
            'level' => $level,
            'student' => $student
        ]);
    }
}

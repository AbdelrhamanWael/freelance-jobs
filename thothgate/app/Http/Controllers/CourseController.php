<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\ExamSession;
use App\Models\Lecture;
use App\Models\PurchasedLectures;
use Illuminate\Support\Facades\Auth;

class CourseController extends Controller
{
    public function main(){
        $courses = Course::where('grade' , Auth::user()->student->grade)->get();
        return view('Courses.courses' , ['courses' => $courses]);
    }

    public function index(string $id)
    {
        $course = Course::findOrFail($id);
        if (Auth::user()->student->grade != $course->grade){
            return redirect()->route( 'courses' )->with('error' , 'You are not allowed to access this course');
        }

        $lectures = Lecture::where('course_id', $id)
            ->with(['purchased_lectures' => function ($query) {
                $query->where('student_id', Auth::user()->student->id);
            }])
            ->get();

        return view('Courses.lectures' , ['lectures' => $lectures , 'course' => $course]);
    }

    public function show($course_id, $lecture)
    {
        $currentLecture = Lecture::findOrFail($lecture);
        if(!$currentLecture){
            return redirect()
                ->route('lectures' , $course_id)
                ->with('error' , 'Lecture not found');
        }
        if ($currentLecture->course->id != $course_id){
            return redirect()
                ->route('lectures' , $course_id)
                ->with('error' , 'this lecture is not for this course');
        }
        if ($currentLecture->course->grade != Auth::user()->student->grade){
            return redirect()
                ->route('courses' , $course_id)
                ->with('error' , 'This Lecture is not for you');
        }
        $valid = PurchasedLectures::where('lecture_id', $lecture)
            ->where('student_id' , Auth::user()->student->id)
            ->first();

        if(!$valid){
            return redirect()->route('buy' , $currentLecture->id);
        }
        
        $course = Course::findOrFail($course_id);
        $lectures = Lecture::where('course_id' , $course_id)->get();
        $session = ExamSession::where('exam_id', $currentLecture->exam->first()->id)
            ->where('student_id', Auth::user()->student->id)
            ->first();

        return view('Courses.lecture' , ['currentLecture' => $currentLecture , 'course' => $course , 'lectures' => $lectures , 'session' => $session]);
    }

    public function buy(string $id)
    {
        $lec = Lecture::where('id' , $id)->first();
        $name = Auth::user()->name;
        $student_id = Auth::user()->student->id;

        $found = PurchasedLectures::where('lecture_id' , $id)
            ->where('student_id' , $student_id)
            ->exists();

        if ($found){
            return redirect()->route('lectures' , $lec->course)->with('error' , 'You have already bought this lecture');
        }

        return view('Courses.buy' , ['lecture' => $lec , 'name' => $name , 'student_id' => $student_id]);;
    }
}

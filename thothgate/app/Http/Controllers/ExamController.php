<?php

namespace App\Http\Controllers;

use App\Models\SessionChoice;
use App\Models\Course;
use App\Models\Exam;
use App\Models\ExamSession;
use App\Models\Lecture;
use App\Models\PurchasedLectures;
use App\Models\Question;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Events\StudentNotification;
use App\Events\AddPoints;
use App\Models\PointsHistroy;
use Carbon\Carbon;

class ExamController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function prepareExam($course_id, $lecture_id)
    {
        $lecture = Lecture::with('exam', 'course')->findOrFail($lecture_id);
        $course = $lecture->course;
        $exam = $lecture->exam->first();

        if (!$exam) {
            return redirect()->route('lectures', [$course, $lecture])->with('error', 'No exam found for this lecture');
        }
        if ($course->grade != Auth::user()->student->grade) {
            return redirect()->route('home')->with('error', 'You are not allowed to access this page');
        }

        // Check if the student already has a session
        $session = ExamSession::where('exam_id', $exam->id)
            ->where('student_id', Auth::user()->student->id)
            ->first();

        if ($session) {
            if ($session->submitted_at) {
                return redirect()->route('home')->with('error', 'You have already submitted your exam');
            }
            return redirect()->route('exam.info', $session->id);
        }
        return view('exam.prepareExam', compact('course', 'lecture', 'exam'));
    }

    public function info($session_id)
    {
        $session = ExamSession::findOrFail($session_id);
        if ($session->student_id != Auth::user()->student->id) {
            return redirect()->route('home')->with('error', 'You are not allowed to access this page');
        }
        return view('exam.info', ['session' => $session]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request, $exam_id, $session_id, $student_id)
    {
        $exam = Exam::with('questions.choices')->findOrFail($exam_id);

        $session = ExamSession::findOrFail($session_id);

        $student = Auth::user()->student;

        if ($session->student_id != Auth::user()->student->id || $session->submitted_at) {
            return redirect()->route('home')->with('error', 'You are not allowed to access this page');
        }

        $answers = $request->input('answers', []);

        $score = 0;
        foreach ($exam->questions as $question) {
            SessionChoice::create([
                'exam_session_id' => $session->id,
                'question_id' => $question->id,
                'choice_id' => $answers[$question->id] ?? null,
            ]);

            if (isset($answers[$question->id])) {
                $selectedChoiceId = $answers[$question->id];

                $correctChoice = $question->choices->firstWhere('is_correct', true);
                if ($correctChoice && $correctChoice->id == $selectedChoiceId) {
                    $score++;
                }
            }
        }

        if($score > 0){
            $student->update(['points' => $student->points + $score]);


            $points = PointsHistroy::create([
                'student_id' => $student_id,
                'points' => $score,
                'reason' => 'Quiz Completeion',
            ]);

            event(new AddPoints($points));
        }

        $session->score = $score;
        $session->submitted_at = now();
        $session->save();

        return redirect()->route('exam.info', $session->id);
    }

    public function show($courseId, $lectureId, $examId)
    {
        $exam = Exam::findOrFail($examId);
        $student = Auth::user()->student;
        $lecture = Lecture::findOrFail($lectureId);
        $purchasedLecture = PurchasedLectures::where('student_id', $student->id)
            ->where('lecture_id', $lectureId)
            ->first();

        if ($student->grade != $exam->lecture->course->grade) {
            return redirect()->route('home')->with('error', 'You are not allowed to access this page');
        }

        $session = ExamSession::where('student_id', $student->id)
            ->where('exam_id', $exam->id)
            ->first();

        if ($session) {
            if ($session->submitted_at) {
                return redirect()->route('exam.info', $session->id)
                    ->with('warning', 'You have already completed this exam.');
            }
        } else {
            $session = ExamSession::create([
                'student_id' => $student->id,
                'exam_id' => $exam->id,
                'started_at' => now(),
                'duration' => $exam->duration,
                'submitted_at' => null,
                'score' => null
            ]);

            if ($purchasedLecture) {
                $purchasedLecture->update(['finished' => true]);

                if(Carbon::now()->lessThanOrEqualTo($lecture->created_at->addDay(3))){
                    Auth::user()->student->update(['points' => $student->points + 15]);
                    PointsHistroy::create([
                        'student_id' => Auth::user()->student->id,
                        'points' => 15,
                        'reason' => 'Complete Lecture within 3 days',
                    ]);
                }

            } else {
                return redirect()->route('home')->with('error', 'you don\'t have access to this exam');
            }
        }

        $questions = Question::with('choices')
            ->where('exam_id', $examId)
            ->get();

        return view('exam.show', [
            'exam' => $exam,
            'questions' => $questions,
            'session' => $session,
        ]);
    }

    public function submit(Course $course, Lecture $lecture, Exam $exam)
    {
        $ongoing = ExamSession::where('student_id', Auth::user()->student_id)
            ->whereNull('submitted_at')
            ->exists();

        $exam_session = ExamSession::where('student_id', Auth::user()->student_id)
            ->where('exam_id', $exam->id)
            ->first();

        if ($ongoing) {
            return redirect()->route('lectures', [$course, $lecture, $exam])
                ->with('error', 'You must finish your ongoing exam before doing anything else.');
        }

        if ($exam_session) {
            return redirect()->route('lectures', [$course, $lecture, $exam])
                ->with('error', 'You have already submitted this exam.');
        }

        return redirect()->route('exam.show', [$course, $lecture, $exam]);
    }

    public function model($session_id)
    {
        $session = ExamSession::findOrFail($session_id);
        $last_choice = SessionChoice::with('choice.question')
            ->where('exam_session_id', $session->id)
            ->get();

        $student = Auth::user()->student;
        $exam = $session->exam;
        $questions = Question::with('choices')->where('exam_id', $exam->id)->get();

        if ($session->student_id != $student->id || !$session->submitted_at) {
            return redirect()->route('home')->with('error', 'You are not allowed to access this page');
        }

        return view('exam.ModelAnswer', [
            'session' => $session,
            'questions' => $questions,
            'last_choice' => $last_choice
        ]);
    }
}

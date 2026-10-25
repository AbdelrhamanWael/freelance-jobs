<?php

namespace App\Http\Controllers;

use App\Models\Community;
use App\Models\CommunityMessage;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Events\MessageEvent;
use App\Models\Exam;
use App\Models\InstructorCourse;
use App\Models\Lecture;
use App\Models\Student;
use App\Events\MessageDeletedEvent;
use App\Models\AdminNotification;
use App\Events\AdminNotificationEvent;
use App\Events\AddPoints;
use App\Events\StudentNotification;
use App\Models\Course;
use App\Models\PointsHistroy;
use App\Models\PurchasedLectures;
use App\Models\StudentPackage;

class InstructorController extends Controller
{
    public function home()
    {
        return view('instructor.home');
    }

    public function addLecture()
    {
        $ins = Auth::user()->instructor;

        $exams = Exam::where('instructor_id', $ins->id)
            ->whereNull('lecture_id')
            ->get();

        $courses = InstructorCourse::where('instructor_id', $ins->id)
            ->join('courses', 'instructor_courses.course_id', '=', 'courses.id')
            ->get(['course_id', 'grade', 'subject']);

        return view('instructor.add-lecture', [
            'exams' => $exams,
            'courses' => $courses,
        ]);
    }

    public function saveLecture(Request $request)
    {
        $validated = $request->validate([
            'video_path' => 'required|string',
            'lecture-title' => 'required|string|max:255',
            'lecture-price' => 'required|integer|min:0',
            'lecture-description' => 'required|string',
            'quiz-name' => 'required|exists:exams,id',
            'grade' => 'required|exists:courses,id',
        ]);

        $videoPath = $validated['video_path'];

        $index = Lecture::where('course_id', $validated['grade'])->count() + 1;

        $lec = Lecture::create([
            'index' => $index,
            'course_id' => $validated['grade'],
            'instructor_id' => Auth::user()->instructor->id,
            'title' => $validated['lecture-title'],
            'video' => $videoPath,
            'price' => $validated['lecture-price'],
            'description' => $validated['lecture-description'],
        ]);

        \App\Jobs\ProcessLectureVideo::dispatch($lec);

        $exam = Exam::findOrFail($validated['quiz-name']);
        $exam->lecture_id = $lec->id;
        $exam->save();


        $notification = AdminNotification::create([
            'title' => Auth::user()->name . " added a new lecture.",
            'is_read' => false,
        ]);

        event(new AdminNotificationEvent($notification));

        $students = StudentPackage::where('course_id', $validated['grade'])
            ->where('remaining', '>', 0)
            ->get();

        $data = [];

        foreach ($students as $std) {
            $data[] = [
                'student_id' => $std->student_id,
                'lecture_id' => $lec->id,
                'course_id' => $lec->course_id,
                'finished' => false,
                'created_at' => now(),
                'updated_at' => now(),
            ];
        }

        PurchasedLectures::insert($data);

        StudentPackage::where('course_id', $lec->course_id)
            ->where('remaining', '>', 0)
            ->decrement('remaining');


        return redirect()->route('instructor.addLecture')->with('success', 'Lecture added successfully!');
    }
public function uploadVideo(Request $request)
{
    $request->validate([
        'lecture-video' => 'required|mimes:mp4,mov,avi,wmv|max:5242880', // 5GB max upload
    ]);

    // This saves the file to 'storage/app/public/lectures' with a unique name
    // and returns the path (e.g., 'lectures/your-unique-filename.mp4').
    $uploadedPath = $request->file('lecture-video')->store('lectures', 'public');

    // All the FFMPEG processing lines have been removed.

    // Return a JSON response with a direct path to the uploaded file.
    return response()->json([
        'success' => true,
        'video_path' => '/storage/' . $uploadedPath,
    ]);
}
    public function createExam()
    {
        $ins = Auth::user()->instructor;

        $grades = InstructorCourse::where('instructor_id', $ins->id)
            ->join('courses', 'instructor_courses.course_id', '=', 'courses.id')
            ->distinct()
            ->pluck('courses.grade');

        return view('instructor.create-exam', ['grades' => $grades]);
    }

    public function saveExam(Request $request)
    {
        $validated = $request->validate([
            'exam-title' => 'required|string|max:255',
            'exam-duration' => 'required|integer|min:1',
            'questions' => 'required|array|min:1',
            'questions.*.text' => 'nullable|string',
            'questions.*.image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048',
            'questions.*.correct_choice' => 'required|numeric',
            'questions.*.choices' => 'required|array|min:2',
            'questions.*.choices.*.text' => 'nullable|string',
            'questions.*.choices.*.image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048',
        ]);


        foreach ($request->questions ?? [] as $qIndex => $question) {
            // Validate choices
            foreach ($question['choices'] ?? [] as $cIndex => $choice) {
                $choiceText = $choice['text'] ?? null;
                $choiceImage = $choice['image'] ?? null;

                if (empty($choiceText) && empty($choiceImage)) {
                    return back()
                        ->withErrors([
                            "questions.$qIndex.choices.$cIndex.text" => "Each choice must have either text or an image."
                        ])
                        ->withInput();
                }
            }

            // Validate question itself
            $questionText = $question['text'] ?? null;
            $questionImage = $question['image'] ?? null;

            if (empty($questionText) && empty($questionImage)) {
                return back()
                    ->withErrors([
                        "questions.$qIndex.text" => "Each question must have either text or an image."
                    ])
                    ->withInput();
            }
        }



        $exam = Exam::create([
            'instructor_id' => Auth::user()->instructor->id,
            'title' => $validated['exam-title'],
            'duration' => $validated['exam-duration'],
        ]);

        foreach ($request->questions as $qId => $qData) {
            $questionImagePath = null;
            if (!empty($qData['image']) && $qData['image'] instanceof \Illuminate\Http\UploadedFile) {
                $questionImagePath = $qData['image']->store('question_images', 'public');
            }

            $question = $exam->questions()->create([
                'text' => $qData['text'] ?? null,
                'image' => $questionImagePath,
            ]);

            foreach ($qData['choices'] ?? [] as $cId => $cData) {
                $choiceImagePath = null;
                if (!empty($cData['image']) && $cData['image'] instanceof \Illuminate\Http\UploadedFile) {
                    $choiceImagePath = $cData['image']->store('choice_images', 'public');
                }

                $question->choices()->create([
                    'text' => $cData['text'] ?? null,
                    'image' => $choiceImagePath,
                    'is_correct' => ((string) $cId === (string) $qData['correct_choice']),
                ]);
            }
        }


        return redirect()->route('instructor.addExam')->with('success', 'Exam created successfully!');
    }


    public function chatsIndex()
    {
        $communities = Community::all();
        return view('instructor.chats', ['communities' => $communities]);
    }
    public function chatShow($community_id)
    {
        $messages = CommunityMessage::where('community_id', $community_id)->get();
        $community = Community::findOrFail($community_id);
        return view('instructor.chat', ['messages' => $messages, 'fullCommunity' => $community]);
    }
    public function MessageStore(Request $request)
    {

        $request->validate([
            'message' => 'nullable|string|max:500',
            'image' => 'nullable|image|max:2048',
            'reply_to' => 'nullable|exists:community_messages,id',
        ]);

        $imagePath = null;

        if ($request->hasFile('image')) {
            $imageName = time() . '_' . $request->file('image')->getClientOriginalName();
            $request->file('image')->move(public_path('community_images'), $imageName);
            $imagePath = 'community_images/' . $imageName;
        }

        if (!$request->message && !$imagePath) {
            return response()->json(['status' => 'Message or image is required!'], 422);
        }

        $message = CommunityMessage::create([
            'user_id' => Auth::user()->id,
            'message' => $request->message,
            'community_id' => $request->community_id,
            'image' => $imagePath,
            'time' => now('Africa/Cairo')->format('h:i A'),
            'reply_to' => $request->reply_to ?? null,
        ]);

        $message->load('user');

        broadcast(new MessageEvent($message))->toOthers();

        return response()->json([
            'status' => 'success',
            'message' => $message
        ]);
    }

    public function destroy($id)
    {
        $message = CommunityMessage::findOrFail($id);

        $message->update([
            'deleted' => true,
            'message' => 'This message was deleted by instructor.',
            'image' => null,
            'reply_to' => null,
        ]);

        broadcast(new MessageDeletedEvent($message))->toOthers();

        return response()->json(['success' => true]);
    }
    public function students()
    {

        $insGrades = InstructorCourse::where('instructor_id', Auth::user()->instructor->id)
            ->join('courses', 'instructor_courses.course_id', '=', 'courses.id')
            ->distinct()
            ->pluck('courses.grade');

        $students = Student::with('user')
            ->whereIn('grade', $insGrades)
            ->get();

        return view('instructor.students', ['grades' => $insGrades, 'students' => $students]);
    }

    public function addPoints($student_id)
    {
        $student = Student::findOrFail($student_id);
        return view('instructor.add-points', ['student' => $student]);
    }
    public function savePoints(Request $request, $student_id)
    {
        $validatedData = $request->validate([
            'pointsAmount' => 'required|numeric|min:1',
            'reason' => 'required|string|max:255',
        ]);

        $student = Student::findOrFail($student_id);

        $student->points += $validatedData['pointsAmount'];
        $student->save();

        $points = PointsHistroy::create([
            'student_id' => $student_id,
            'points' => $validatedData['pointsAmount'],
            'reason' => $validatedData['reason'],
        ]);

        event(new AddPoints($points));
        event(new StudentNotification($student->id, 'You have earned ' . $validatedData['pointsAmount'] . ' points.'));


        return response()->json([
            'status' => 'success',
        ]);

    }
}

<?php

use App\Http\Controllers\CommunityController;
use App\Http\Controllers\ContactController;
use App\Http\Controllers\CourseController;
use App\Http\Controllers\EmailController;
use App\Http\Controllers\ExamController;
use App\Http\Controllers\LoginController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\RegisterController;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\InstructorController;
use App\Models\Course;
use App\Http\Controllers\VideoController;


//login
Route::get('/login', [LoginController::class, 'index'])->name('login')->middleware('guest');
Route::post('/login', [LoginController::class, 'store'])->middleware('guest');
Route::delete('/logout', [LoginController::class, 'destroy']);

Route::get('/logout' , function(){
    abort(404);
});

//register
Route::get('/register', [RegisterController::class, 'index'])->middleware('guest');
Route::post('/register', [RegisterController::class, 'store'])->middleware('guest');

// Verifications
Route::get('email/verify', [EmailController::class, 'waiting'])
    ->middleware('auth')
    ->name('verification.notice');

Route::get('/email/verify/{id}/{hash}', [EmailController::class, 'verify'])
    ->middleware(['auth', 'signed'])
    ->name('verification.verify');

Route::post('/email/verification-notification', [EmailController::class, 'resend'])
    ->middleware(['auth', 'throttle:6,1'])
    ->name('verification.send');

// home page
Route::get('/', function () {
    $courses1 = Course::where('grade', 'Third Preparatory')->get();
    $courses2 = Course::where('grade', 'First Secondary')->get();
    return view('welcome', ['courses1' => $courses1, 'courses2' => $courses2]);
})->middleware('guest')->name('welcome');

Route::view('/privacy', 'privacy');

// students
Route::middleware(['auth', 'student', 'prevent.multiple.logins'])->group(function () {
    // home page
    Route::view('/student/home', 'home')
        ->name('home');

    //profile
    Route::get('/profile', [ProfileController::class, 'index'])
        ->name('profile');

    Route::delete('profile/delete/{student}', [ProfileController::class, 'destroy']);

    Route::get('profile/points-history', [ProfileController::class, 'pointsHistory'])->name('student.pointsHistory');
    Route::get('profile/levels', [ProfileController::class, 'levels'])->name('student.levels');

    // courses
    Route::middleware(['verified', 'check.exam'])->group(function () {
        Route::get('courses', [CourseController::class, 'main'])->name('courses');
        Route::get('courses/{course}', [CourseController::class, 'index'])->name('lectures');
        Route::get('lectures/{lecture}/buy', [CourseController::class, 'buy'])->name('buy');
        Route::get('lectures/{course}/{lecture}', [CourseController::class, 'show'])->name('lectures.show');
        Route::get('/video/{filename}', [VideoController::class, 'streamVideo']);
    });
    // contact
    Route::get('/contact', [ContactController::class, 'index'])
        ->middleware(['verified', 'check.exam'])
        ->name('contact.index');

    Route::post('/contact', [ContactController::class, 'store'])
        ->middleware(['verified', 'check.exam']);

    // community
    Route::get('/community', [CommunityController::class, 'index'])
        ->middleware(['verified', 'check.exam'])
        ->name('community');

    Route::post('/community', [CommunityController::class, 'store'])
        ->middleware(['verified', 'check.exam'])
        ->name('community.store');

    Route::delete('/community/message/{id}', [CommunityController::class, 'destroy'])
        ->name('community.message.destroy');

    // exams
    Route::prefix('courses/{course}/{lecture}/exams')->middleware('verified')->group(function () {
        Route::get('/', [ExamController::class, 'prepareExam'])->name('exam.prepareExam');
        Route::get('{exam}', [ExamController::class, 'show'])->name('exam.show');
        Route::post('{exam}/submit', [ExamController::class, 'submit']);
    });
    Route::post('/submit/{exam}/{session}/{student}', [ExamController::class, 'store'])
        ->middleware('verified')
        ->name('exam.store');

    Route::get('info/{session}', [ExamController::class, 'info'])
        ->middleware('verified')
        ->name('exam.info');

    Route::get('info/model/{session}', [ExamController::class, 'model'])
        ->middleware('verified')
        ->name('exam.model');
});

// Admin routes
Route::middleware(['auth', 'check.admin'])->group(function () {
    // home
    Route::get('/admin/home', [AdminController::class, 'home'])
        ->name('admin.home');

    Route::get('/students/export', [AdminController::class, 'exportStudents'])
        ->name('students.export');

    Route::get('/instructors/export', [AdminController::class, 'exportInstructors'])
        ->name('instructors.export');


    Route::get('/admin/edit-password' , [AdminController::class, 'editPassword'])->name('editAdminPassword');

    Route::post('/admin/edit-password' , [AdminController::class, 'savePassword'])->name('saveAdminPassword');


    //instructors
    Route::get('/admin/instructors', [AdminController::class, 'instructors'])
        ->name('admin.instructors');

    Route::get('/admin/instructors/create', [AdminController::class, 'createInstructorIndex'])
        ->name('instructors.create');

    Route::post('/admin/instructors/create', [AdminController::class, 'createInstructor']);

    Route::delete('admin/instructors/{instructor}', [AdminController::class, 'destroyInstructor'])
        ->name('instructors.destroy');

    //students
    Route::get('/admin/students', [AdminController::class, 'students'])
        ->name('admin.students');

    Route::get('/admin/students/{student}', [AdminController::class, 'showStudent'])
        ->name('students.show');

    Route::delete('/admin/students/{student}', [AdminController::class, 'destroyStudent'])
        ->name('students.destroy');

    Route::post('/open/lecture/{student}', [AdminController::class, 'grantAccess']);

    Route::post('open/package/{student}', [AdminController::class, 'grantPackage'])
        ->name('grantPackage');

    Route::delete('/remove/lecture/{student}', [AdminController::class, 'removeAccess']);

    Route::post('/edit-end-date/{student}', [AdminController::class, 'editEndDate']);

    Route::get('/admin/exams/{student}', [AdminController::class, 'StudentExams']);

    Route::get('/admin/model/{session}', [AdminController::class, 'StudentModel']);

    Route::get('/export/exams/{student}', [AdminController::class, 'exportStudentsExams'])
        ->name('students.exams.export');

    //notifications
    Route::get('/admin/notifications', [AdminController::class, 'notifications'])->name('admin.notifications');

    Route::post('/read-all', [AdminController::class, 'readAll']);

    Route::post('/read/{notification}', [AdminController::class, 'readNotification']);

    Route::delete('delete/{notification}', [AdminController::class, 'deleteNotification']);

    //messages
    Route::get('admin/messages', [AdminController::class, 'messagesView'])->name('admin.messages');

    Route::delete('/message/delete/{message}', [AdminController::class, 'deleteMessage']);

    //courses
    Route::get('/admin/courses' , [AdminController::class, 'courses'])->name('admin.course');
    Route::get('/admin/addCourse' , [AdminController::class , 'addCourse'])->name('admin.addCourse');
    Route::post('/admin/addCourse' , [AdminController::class , 'saveCourse'])->name('admin.saveCourse');
    Route::get('/admin/courses/{lectures}', [AdminController::class, 'lectures'])->name('admin.lectures');
    Route::delete('/admin/courses/{lectures}', [AdminController::class, 'destroyLecture'])->name('admin.destroyLecture');

});
// Instructor routes
Route::middleware(['auth', 'check.instructor'])->group(function () {

    // home
    Route::get('/instructor/home', [InstructorController::class, 'home'])
        ->name('instructors.home');

    //add lecture
    Route::get('/instructor/add/lecture', [InstructorController::class, 'addLecture'])
        ->name('instructor.addLecture');

    Route::post('/instructor/add/lecture', [InstructorController::class, 'saveLecture']);

    Route::post('/instructor/upload-video', [InstructorController::class, 'uploadVideo']);


    //create exam
    Route::get('/instructor/create/exam', [InstructorController::class, 'createExam'])
        ->name('instructor.addExam');

    Route::post('/instructor/create/exam', [InstructorController::class, 'saveExam']);

    // chats
    Route::get('/instructor/chats', [InstructorController::class, 'chatsIndex'])
        ->name('instructor.chats');

    Route::post('/instructor/chats', [InstructorController::class, 'MessageStore'])
        ->name('chat.store');

    Route::get('instructor/chats/{community}', [InstructorController::class, 'chatShow']);

    Route::delete('/instructor/chats/delete/{Id}', [InstructorController::class, 'destroy']);

    //points
    Route::get('/instructor/students', [InstructorController::class, 'students'])
        ->name('instructor.students');

    Route::get('/instructor/add/points/{student}', [InstructorController::class, 'addPoints'])
        ->name('instructor.addPoints');

    Route::post('/instructor/add/points/{student}', [InstructorController::class, 'savePoints'])
        ->name('instructor.savePoints');
});

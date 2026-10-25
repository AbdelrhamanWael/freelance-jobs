<?php

namespace App\Http\Controllers;

use App\Models\Student;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Session;
use App\Events\AdminNotificationEvent;
use App\Models\AdminNotification;
use App\Models\PointsHistroy;
use App\Events\AddPoints;


class RegisterController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return view('auth.register');
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'phone_number' => 'required|string|max:255',
            'dateOfBirth' => 'required|date',
            'password' => 'required|string|min:8|confirmed',
            'grade' => 'required|string|in:Third Preparatory,First Secondary',
        ]);


        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'phone_number' => $request->phone_number,
            'date_of_birth' => $request->dateOfBirth,
            'password' => bcrypt($request->password),
            'type' => 0,
            'email_verified_at' => now(),
        ]);

        $user->student()->create([
            'grade' => $request->grade,
            'points' => 20,
        ]);

        Auth::login($user);
        $request->session()->regenerate();
        $user->session_id = Session::getId();
        $user->save();

        $notification = AdminNotification::create([
            'title' => "New student registered",
            'is_read' => false,
        ]);
        event(new AdminNotificationEvent($notification));

        $points = PointsHistroy::create([
            'student_id' => $user->student->id,
            'points' => 20,
            'reason' => 'Welcome Bonus',
        ]);

        event(new AddPoints($points));

        return redirect()->route('home');
    }
}

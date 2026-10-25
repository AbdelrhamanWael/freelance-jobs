<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Session;
use App\Models\User;

class LoginController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return view('auth.login');
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'email' => 'required|string|email',
            'password' => '',
        ]);
        if (Auth::attempt($request->only('email', 'password'))){
            $request->session()->regenerate();
            $user = User::find(Auth::id());
            $user->session_id = Session::getId();
            $user->save();

            if ($user->type == 2) {
                return redirect()->route('admin.home');
            }
            else if ($user->type == 1) {
                return redirect()->route('instructors.home');
            }
            return redirect()->route('home');
        }
        return back()->withErrors([
            'email' => 'Wrong credentials, please try again.',
        ])->withInput($request->only('email'));
    }
    /**
     * Remove the specified resource from storage.
     */
    public function destroy()
    {
	if(Auth::guest()){
            return redirect()->route('login');
        }
        Auth::logout();
        return redirect()->route('welcome');
    }
}

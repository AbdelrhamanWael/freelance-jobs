<?php

namespace App\Http\Controllers;

use App\Events\ContactMessage;
use App\Models\Contact;
use Illuminate\Contracts\Support\ValidatedData;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Events\AdminNotificationEvent;
use App\Models\AdminNotification;

class ContactController extends Controller
{
    public function index()
    {
        return view('Contact');
    }

    public function store(Request $request)
    {

        $contact = Contact::create([
            'user_id' => Auth::id(),
            'subject' => $request->input('subject'),
            'message' => $request->input('message'),
        ]);

        $notification = AdminNotification::create([
            'title' => "New contact message from " . Auth::user()->name,
            'is_read' => false,
        ]);

        event(new AdminNotificationEvent($notification));

        event(new ContactMessage($contact, Auth::user()));

        return response()->json([
            'status' => 'success',
            'message' => 'Message sent successfully'
        ]);
    }
}

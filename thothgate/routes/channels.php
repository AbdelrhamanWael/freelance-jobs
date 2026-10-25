<?php

use Illuminate\Support\Facades\Broadcast;

Broadcast::channel('App.Models.User.{id}', function ($user, $id) {
    return (int) $user->id === (int) $id;
});

Broadcast::channel('student.{studentId}', function ($user, $student_id) {
    return $user->student && (int) $user->student->id === (int) $student_id;
});

Broadcast::channel('student.notification.{studentId}', function ($user, $student_id) {
    return $user->student && (int) $user->student->id === (int) $student_id;
});

Broadcast::channel('AddPoints.{studentId}', function ($user, $studentId) {
    return $user->student && $user->student->id == (int) $studentId;
});
<?php

use App\Models\User;
use App\Models\Instructor;
use App\Models\Course;
use App\Models\InstructorCourse;
use App\Models\Exam;

// 1. Upgrade everyone to an Instructor (type = 1)
$users = User::all();
foreach ($users as $u) {
    if ($u->type != 2) { // don't override admin
        $u->type = 1;
        $u->save();
        $ins = Instructor::firstOrCreate(['user_id' => $u->id]);
        
        // 2. Create a test course so they have something in the dropdown
        $c = Course::firstOrCreate([
            'subject' => 'HLS Video Test Course', 
            'grade' => 'First Secondary', 
            'teacher' => $u->name, 
            'image' => 'imgs/logo.png'
        ]);

        InstructorCourse::firstOrCreate([
            'instructor_id' => $ins->id, 
            'course_id' => $c->id
        ]);

        // 3. Exam is needed because the "Add Lecture" form requires assigning to a quiz!
        Exam::firstOrCreate(
            ['instructor_id' => $ins->id, 'title' => 'Test Video Quiz'],
            ['duration' => 10]
        );
    }
}

echo "All regular users have been upgraded to Instructors and given a Test Course to upload into!\n";

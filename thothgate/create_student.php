<?php
use App\Models\User;
use Illuminate\Support\Facades\DB;

try {
    $u = User::where('email', 'student@test.com')->first();
    if ($u) {
        $studentExists = DB::table('students')->where('user_id', $u->id)->first();
        if (!$studentExists) {
            $studentId = DB::table('students')->insertGetId([
                'user_id' => $u->id,
                'grade' => 'First Secondary',
                'points' => 10000,
                'created_at' => now(),
                'updated_at' => now()
            ]);
        } else {
            $studentId = $studentExists->id;
        }

        $lecture = DB::table('lectures')->first();
        if ($lecture) {
            $purchaseExists = DB::table('purchased_lectures')
                ->where('student_id', $studentId)
                ->where('lecture_id', $lecture->id)
                ->first();
            if (!$purchaseExists) {
                DB::table('purchased_lectures')->insert([
                    'student_id' => $studentId,
                    'lecture_id' => $lecture->id,
                    'course_id' => $lecture->course_id, // Fix missing course_id!
                    'created_at' => now(),
                    'updated_at' => now()
                ]);
            }
            echo "Lecture purchased for student.\n";
        }
        
        echo "Student fixed.\n";
    } else {
        echo "User not found.\n";
    }
} catch (\Exception $e) {
    echo "ERROR: " . $e->getMessage() . "\n";
}

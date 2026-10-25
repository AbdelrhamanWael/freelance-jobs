<?php

namespace Database\Seeders;

use App\Models\Instructor;
use App\Models\Student;
use App\Models\User;
use App\Models\InstructorCourse;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call(CourseSeeder::class);

        User::factory()->create([
            'name' => 'Ammar Mohamed Ali',
            'date_of_birth' => '1999-01-01',
            'password' => bcrypt('11111111'),
            'email_verified_at' => now(),
            'email' => 'ammar@gmail.com',
            'phone_number' => '01129264191',
            'type' => 0,
        ]);
        Student::create([
            'user_id' => 1,
            'grade' => 'Third Preparatory',
            'points'=> 0,
        ]);

        User::factory()->create([
            'name' => 'Mohamed Ahmed',
            'date_of_birth' => '2005-01-01',
            'password' => bcrypt('11111111'),
            'email_verified_at' => now(),
            'email' => 'mohamed@gmail.com',
            'phone_number' => '01129264191',
            'type' => 0,
        ]);
        Student::create([
            'user_id' => 2,
            'grade' => 'Third Preparatory',
            'points'=> 0,
        ]);

        User::factory()->create([
            'name' => 'Admin',
            'date_of_birth' => '2000-01-01',
            'password' => bcrypt('11111111'),
            'email_verified_at' => now(),
            'email' => 'admin@gmail.com',
            'phone_number' => '01129264191',
            'type' => 2,
        ]);
    }
}

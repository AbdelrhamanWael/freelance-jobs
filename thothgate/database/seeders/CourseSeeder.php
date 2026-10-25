<?php

namespace Database\Seeders;

use App\Models\Community;
use App\Models\Course;
use Illuminate\Database\Seeder;

class CourseSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        Course::truncate();
        $courses = [
            [
                'subject' => 'Arabic',
                'grade' => 'Third Preparatory',
                'teacher' => 'Mostafa badr',
                'image' => 'imgs/language.jpg',
            ],
            [
                'subject' => 'English',
                'grade' => 'Third Preparatory',
                'teacher' => 'Alaa Rady',
                'image' => 'imgs/english.jpg',
            ],
            [
                'subject' => 'رياضيات',
                'grade' => 'Third Preparatory',
                'teacher' => 'Amir Ayman',
                'image' => 'imgs/maths.jpg',
            ],
            [
                'subject' => 'Math',
                'grade' => 'Third Preparatory',
                'teacher' => 'Ayman nessiem',
                'image' => 'imgs/maths.jpg',
            ],
            [
                'subject' => 'علوم',
                'grade' => 'Third Preparatory',
                'teacher' => 'Bassam',
                'image' => 'imgs/science.jpg',
            ],
            [
                'subject' => 'دراسات إجتماعية',
                'grade' => 'Third Preparatory',
                'teacher' => 'Alaa',
                'image' => 'imgs/socialStudies.jpg',
            ],
            [
                'subject' => 'Italian',
                'grade' => 'Third Preparatory',
                'teacher' => 'Alaa Rady',
                'image' => 'imgs/italian.jpg',
            ],
            [
                'subject' => 'French',
                'grade' => 'Third Preparatory',
                'teacher' => 'Raffqa',
                'image' => 'imgs/french.jpg',
            ],

            // Courses for First Secondary
            [
                'subject' => 'Arabic',
                'grade' => 'First Secondary',
                'teacher' => 'Mostafa Badr',
                'image' => 'imgs/arabic.jpg',
            ],
            [
                'subject' => 'English',
                'grade' => 'First Secondary',
                'teacher' => 'Alaa Rady',
                'image' => 'imgs/english.jpg',
            ],
            [
                'subject' => 'Philosophy & Logic',
                'grade' => 'First Secondary',
                'teacher' => 'none',
                'image' => 'imgs/philosophy.jpg',
            ],
            [
                'subject' => 'History',
                'grade' => 'First Secondary',
                'teacher' => 'Alaa',
                'image' => 'imgs/history.jpg',
            ],
            [
                'subject' => 'رياضيات',
                'grade' => 'First Secondary',
                'teacher' => 'Shenouda Shouky',
                'image' => 'imgs/math.jpg',
            ],
            [
                'subject' => 'Mathematics',
                'grade' => 'First Secondary',
                'teacher' => 'Ayman Nessiem',
                'image' => 'imgs/math.jpg',
            ],
            [
                'subject' => 'علوم متكاملة',
                'grade' => 'First Secondary',
                'teacher' => 'Bassam',
                'image' => 'imgs/integratedScience.jpg',
            ],
            [
                'subject' => 'Italian',
                'grade' => 'First Secondary',
                'teacher' => 'Alaa Rady',
                'image' => 'imgs/italian.jpg',
            ],
            [
                'subject' => 'French',
                'grade' => 'First Secondary',
                'teacher' => 'Raffqa',
                'image' => 'imgs/french.jpg',
            ],
        ];

        $communities = [
            [
                'grade' => 'Third Preparatory',
            ],
            [
                'grade' => 'First Secondary',
            ],
        ];

        foreach ($communities as $community) {
            Community::create($community);
        }
    }
}

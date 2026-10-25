<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Course extends Model
{
    protected $guarded = [];
    protected $table = 'courses';

    public function lectures()
    {
        return $this->hasMany(Lecture::class);
    }
    public function purchased_lectures(){
        return $this->hasMany(PurchasedLectures::class);
    }
    public function instructors(){
        return $this->hasMany(InstructorCourse::class);
    }
    
    public function packages(){
        return $this->hasMany(StudentPackage::class);
    }
}

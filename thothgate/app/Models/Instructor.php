<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Instructor extends Model
{
    protected $guarded = [];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
    public function lectures()
    {
        return $this->hasMany(Lecture::class);
    }
    public function courses(){
        return $this->hasMany(InstructorCourse::class);
    }
    public function exams(){
        return $this->hasMany(Exam::class);
    }
}

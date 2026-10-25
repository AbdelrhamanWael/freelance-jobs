<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class InstructorCourse extends Model
{
    protected $guarded = [];

    public function instructor(){
        return $this->belongsTo(Instructor::class);
    }

    public function course(){
        return $this->belongsTo(Course::class);
    }
}

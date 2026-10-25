<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class StudentPackage extends Model
{
    protected $guarded = [];
    
    public function student(){
        return $this->belongsTo(Student::class);
    }

    public function course(){
        return $this->belongsTo(Course::class);
    }
}

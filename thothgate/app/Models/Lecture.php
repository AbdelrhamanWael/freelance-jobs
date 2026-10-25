<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Lecture extends Model
{
    protected $guarded = [];
    protected $table = 'lectures';
    public function instructor()
    {
        return $this->belongsTo(Instructor::class);
    }
    public function purchased_lectures()
    {
        return $this->hasMany(PurchasedLectures::class);
    }
    public function course()
    {
        return $this->belongsTo(Course::class);
    }
    public function exam()
    {
        return $this->hasMany(Exam::class);
    }
}

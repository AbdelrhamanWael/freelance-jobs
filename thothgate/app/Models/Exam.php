<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Exam extends Model
{
    protected $guarded = [];
    protected $table = 'exams';
    public function lecture()
    {
        return $this->belongsTo(Lecture::class);
    }
    public function questions()
    {
        return $this->hasMany(Question::class);
    }
    public function exam_sessions()
    {
        return $this->hasMany(ExamSession::class);
    }
    public function instructor(){
        return $this->belongsTo(Instructor::class);
    }
}

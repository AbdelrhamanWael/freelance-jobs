<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ExamSession extends Model
{
    protected $casts = [
        'started_at' => 'datetime',
        'submitted_at' => 'datetime',
    ];
    protected $guarded = [];
    protected $table = 'exam_sessions';
    public function exam()
    {
        return $this->belongsTo(Exam::class);
    }
    public function student()
    {
        return $this->belongsTo(Student::class);
    }
    public function choices()
    {
        return $this->hasMany(SessionChoice::class, 'session_id');
    }
}

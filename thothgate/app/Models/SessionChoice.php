<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SessionChoice extends Model
{
    protected $guarded = [];

    public function examSession()
    {
        return $this->belongsTo(ExamSession::class);
    }

    public function question()
    {
        return $this->belongsTo(Question::class);
    }
    
    public function choice(){
        return $this->belongsTo(Choice::class);
    }
}

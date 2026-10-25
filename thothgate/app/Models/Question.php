<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Question extends Model
{
    protected $guarded = [];
    protected $table = 'questions';
    public function exam()
    {
        return $this->belongsTo(Exam::class);
    }
    public function choices()
    {
        return $this->hasMany(Choice::class);
    }
    public function sessions()
    {
        return $this->hasMany(SessionChoice::class);
    }
}

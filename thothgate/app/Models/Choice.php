<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Choice extends Model
{
    protected $guarded = [];
    protected $table = 'choices';
    public function question()
    {
        return $this->belongsTo(Question::class);
    }
    public function sessions()
    {
        return $this->hasMany(SessionChoice::class);
    }
}

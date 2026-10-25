<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PointsHistroy extends Model
{
    protected $guarded = [];
    
    public function student(){
        return $this->belongsTo(Student::class);
    }
}

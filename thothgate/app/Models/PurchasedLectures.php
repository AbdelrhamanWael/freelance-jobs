<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PurchasedLectures extends Model
{
    protected $guarded = [];
    protected $table = 'purchased_lectures';
    public function student()
    {
        return $this->belongsTo(Student::class);
    }
    public function lecture()
    {
        return $this->belongsTo(Lecture::class);
    }
    public function course()
    {
        return $this->belongsTo(Course::class);
    }
}

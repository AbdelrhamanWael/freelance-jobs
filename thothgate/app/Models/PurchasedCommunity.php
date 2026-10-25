<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PurchasedCommunity extends Model
{
    protected $guarded = [];
    protected $table = 'purchased_communities';
    public function student()
    {
        return $this->belongsTo(Student::class);
    }
    public function community()
    {
        return $this->belongsTo(Community::class);
    }
}
